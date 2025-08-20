"""
Utilities for calculating CO2 emissions based on changes in carbon stocks (e.g., `organicCarbonPerHa`,
`aboveGroundBiomass` and `belowGroundBiomass`).
"""
from datetime import datetime
from enum import Enum
from functools import reduce
from itertools import product
from numpy import array, random, mean
from numpy.typing import NDArray
from pydash.objects import merge
from typing import Any, Callable, NamedTuple, Optional, Union
from hestia_earth.schema import (
    EmissionMethodTier, EmissionStatsDefinition, MeasurementMethodClassification
)
from hestia_earth.utils.date import diff_in_days, YEAR
from hestia_earth.utils.tools import flatten, non_empty_list, safe_parse_date
from hestia_earth.utils.stats import correlated_normal_2d, gen_seed
from hestia_earth.utils.descriptive_stats import calc_descriptive_stats

from hestia_earth.models.log import log_as_table
from hestia_earth.models.utils import pairwise
from hestia_earth.models.utils.blank_node import (
    _gapfill_datestr, _get_datestr_format, DatestrGapfillMode, DatestrFormat, group_nodes_by_year, node_term_match,
    split_node_by_dates
)
from hestia_earth.models.utils.constant import Units, get_atomic_conversion
from hestia_earth.models.utils.emission import min_emission_method_tier
from hestia_earth.models.utils.measurement import (
    group_measurements_by_method_classification, min_measurement_method_classification,
    to_measurement_method_classification
)
from hestia_earth.models.utils.site import related_cycles
from hestia_earth.models.utils.time_series import (
    calc_tau, compute_time_series_correlation_matrix, exponential_decay
)

from .utils import check_consecutive
from . import MODEL

_ITERATIONS = 10000
_MAX_CORRELATION = 1
_MIN_CORRELATION = 0.5
_NOMINAL_ERROR = 75
"""
Carbon stock measurements without an associated `sd` should be assigned a nominal error of 75% (2*sd as a percentage of
the mean).
"""
_TRANSITION_PERIOD_YEARS = 20
_TRANSITION_PERIOD_DAYS = 20 * YEAR  # 20 years in days
_VALID_DATE_FORMATS = {
    DatestrFormat.YEAR,
    DatestrFormat.YEAR_MONTH,
    DatestrFormat.YEAR_MONTH_DAY,
    DatestrFormat.YEAR_MONTH_DAY_HOUR_MINUTE_SECOND
}

DEFAULT_MEASUREMENT_METHOD_RANKING = [
    MeasurementMethodClassification.ON_SITE_PHYSICAL_MEASUREMENT,
    MeasurementMethodClassification.MODELLED_USING_OTHER_MEASUREMENTS,
    MeasurementMethodClassification.TIER_3_MODEL,
    MeasurementMethodClassification.TIER_2_MODEL,
    MeasurementMethodClassification.TIER_1_MODEL
]
"""
The list of `MeasurementMethodClassification`s that can be used to calculate carbon stock change emissions, ranked in
order from strongest to weakest.
"""

_DEFAULT_EMISSION_METHOD_TIER = EmissionMethodTier.TIER_1
_MEASUREMENT_METHOD_CLASSIFICATION_TO_EMISSION_METHOD_TIER = {
    MeasurementMethodClassification.TIER_2_MODEL: EmissionMethodTier.TIER_2,
    MeasurementMethodClassification.TIER_3_MODEL: EmissionMethodTier.TIER_3,
    MeasurementMethodClassification.MODELLED_USING_OTHER_MEASUREMENTS: EmissionMethodTier.MEASURED,
    MeasurementMethodClassification.ON_SITE_PHYSICAL_MEASUREMENT: EmissionMethodTier.MEASURED,
}
"""
A mapping between `MeasurementMethodClassification`s and `EmissionMethodTier`s. As carbon stock measurements can be
measured/estimated through a variety of methods, the emission model needs be able to assign an emission tier for each.
Any `MeasurementMethodClassification` not in the mapping should be assigned `DEFAULT_EMISSION_METHOD_TIER`.
"""


class _InventoryKey(Enum):
    """
    The inner keys of the annualised inventory created by the `_compile_inventory` function.

    The value of each enum member is formatted to be used as a column header in the `log_as_table` function.
    """
    CARBON_STOCK = "carbon-stock"
    CARBON_STOCK_CHANGE = "carbon-stock-change"
    CO2_EMISSION = "carbon-emission"
    SHARE_OF_EMISSION = "share-of-emissions"
    LAND_USE_SUMMARY = "land-use-summary"
    LAND_USE_CHANGE_EVENT = "luc-event"
    YEARS_SINCE_LUC_EVENT = "years-since-luc-event"
    YEARS_SINCE_INVENTORY_START = "years-since-inventory-start"


CarbonStock = NamedTuple("CarbonStock", [
    ("value", NDArray),
    ("date", str),
    ("method", MeasurementMethodClassification)
])
"""
NamedTuple representing a carbon stock (e.g., `organicCarbonPerHa` or `aboveGroundBiomass`).

Attributes
----------
value : NDArray
    The value of the carbon stock measurement (kg C ha-1).
date : str
    The date of the measurement as a datestr with the format `YYYY`, `YYYY-MM`, `YYYY-MM-DD` or `YYYY-MM-DDTHH:mm:ss`.
method: MeasurementMethodClassification
    The measurement method for the carbon stock.
"""


CarbonStockChange = NamedTuple("CarbonStockChange", [
    ("value", NDArray),
    ("start_date", str),
    ("end_date", str),
    ("method", MeasurementMethodClassification)
])
"""
NamedTuple representing a carbon stock change.

Attributes
----------
value : NDArray
    The value of the carbon stock change (kg C ha-1).
start_date : str
    The start date of the carbon stock change event as a datestr with the format `YYYY`, `YYYY-MM`, `YYYY-MM-DD` or
    `YYYY-MM-DDTHH:mm:ss`.
end_date : str
    The end date of the carbon stock change event as a datestr with the format `YYYY`, `YYYY-MM`, `YYYY-MM-DD` or
    `YYYY-MM-DDTHH:mm:ss`.
method: MeasurementMethodClassification
    The measurement method for the carbon stock change.
"""


CarbonStockChangeEmission = NamedTuple("CarbonStockChangeEmission", [
    ("value", NDArray),
    ("start_date", str),
    ("end_date", str),
    ("method", EmissionMethodTier)
])
"""
NamedTuple representing a carbon stock change emission.

Attributes
----------
value : NDArray
    The value of the carbon stock change emission (kg CO2 ha-1).
start_date : str
    The start date of the carbon stock change emission as a datestr with the format `YYYY`, `YYYY-MM`, `YYYY-MM-DD` or
    `YYYY-MM-DDTHH:mm:ss`.
end_date : str
    The end date of the carbon stock change emission as a datestr with the format `YYYY`, `YYYY-MM`, `YYYY-MM-DD` or
    `YYYY-MM-DDTHH:mm:ss`.
method: MeasurementMethodClassification
    The emission method tier.
"""


def _lerp_carbon_stocks(start: CarbonStock, end: CarbonStock, target_date: str) -> CarbonStock:
    """
    Estimate, using linear interpolation, a carbon stock for a specific date based on the carbon stocks of two other
    dates.

    Parameters
    ----------
    start : CarbonStock
        The `CarbonStock` at the start (kg C ha-1).
    end : CarbonStock
        The `CarbonStock` at the end (kg C ha-1).
    target_date : str
        The target date for interpolation as a datestr with format `YYYY`, `YYYY-MM`, `YYYY-MM-DD` or
    `YYYY-MM-DDTHH:mm:ss`.

    Returns
    -------
    CarbonStock
        The interpolated `CarbonStock` for the specified date (kg C ha-1).
    """
    alpha = diff_in_days(start.date, target_date) / diff_in_days(start.date, end.date)
    value = (1 - alpha) * start.value + alpha * end.value
    method = min_measurement_method_classification(start.method, end.method)
    return CarbonStock(value, target_date, method)


def _calc_carbon_stock_change(start: CarbonStock, end: CarbonStock) -> CarbonStockChange:
    """
    Calculate the change in a carbon stock between two different dates.

    The method should be the weaker of the two `MeasurementMethodClassification`s.

    Parameters
    ----------
    start : CarbonStock
        The carbon stock at the start (kg C ha-1).
    end : CarbonStock
        The carbon stock at the end (kg C ha-1).

    Returns
    -------
    CarbonStockChange
        The carbon stock change (kg C ha-1).
    """
    value = end.value - start.value
    method = min_measurement_method_classification(start.method, end.method)
    return CarbonStockChange(value, start.date, end.date, method)


def _calc_carbon_stock_change_emission(carbon_stock_change: CarbonStockChange) -> CarbonStockChangeEmission:
    """
    Convert a `CarbonStockChange` into a `CarbonStockChangeEmission`.

    Parameters
    ----------
    carbon_stock_change : CarbonStockChange
        The carbon stock change (kg C ha-1).

    Returns
    -------
    CarbonStockChangeEmission
        The carbon stock change emission (kg CO2 ha-1).
    """
    value = _convert_c_to_co2(carbon_stock_change.value) * -1
    method = _convert_mmc_to_emt(carbon_stock_change.method)
    return CarbonStockChangeEmission(value, carbon_stock_change.start_date, carbon_stock_change.end_date, method)


def _convert_mmc_to_emt(
    measurement_method_classification: MeasurementMethodClassification
) -> EmissionMethodTier:
    """
    Get the emission method tier based on the provided measurement method classification.

    Parameters
    ----------
    measurement_method_classification : MeasurementMethodClassification
        The measurement method classification to convert into the corresponding emission method tier.

    Returns
    -------
    EmissionMethodTier
        The corresponding emission method tier.
    """
    return _MEASUREMENT_METHOD_CLASSIFICATION_TO_EMISSION_METHOD_TIER.get(
        to_measurement_method_classification(measurement_method_classification),
        _DEFAULT_EMISSION_METHOD_TIER
    )


def _convert_c_to_co2(kg_c: float) -> float:
    """
    Convert mass of carbon (C) to carbon dioxide (CO2) using the atomic conversion ratio.

    n.b. `get_atomic_conversion` returns the ratio C:CO2 (~44/12).

    Parameters
    ----------
    kg_c : float
        Mass of carbon (C) to be converted to carbon dioxide (CO2) (kg C).

    Returns
    -------
    float
        Mass of carbon dioxide (CO2) resulting from the conversion (kg CO2).
    """
    return kg_c * get_atomic_conversion(Units.KG_CO2, Units.TO_C)


def _rescale_carbon_stock_change_emission(
    emission: CarbonStockChangeEmission, factor: float
) -> CarbonStockChangeEmission:
    """
    Rescale a `CarbonStockChangeEmission` by a specified factor.

    Parameters
    ----------
    emission : CarbonStockChangeEmission
        A carbon stock change emission (kg CO2 ha-1).
    factor : float
        A scaling factor, representing a proportion of the total emission as a decimal. (e.g., a
        [Cycles](https://www.hestia.earth/schema/Cycle)'s share of an annual emission).

    Returns
    -------
    CarbonStockChangeEmission
        The rescaled emission.
    """
    value = emission.value * factor
    return CarbonStockChangeEmission(value, emission.start_date, emission.end_date, emission.method)


def _add_carbon_stock_change_emissions(
    emission_1: CarbonStockChangeEmission, emission_2: CarbonStockChangeEmission
) -> CarbonStockChangeEmission:
    """
    Sum together multiple `CarbonStockChangeEmission`s.

    Parameters
    ----------
    emission_1 : CarbonStockChangeEmission
        A carbon stock change emission (kg CO2 ha-1).
    emission_2 : CarbonStockChangeEmission
        A carbon stock change emission (kg CO2 ha-1).

    Returns
    -------
    CarbonStockChangeEmission
        The summed emission.
    """
    value = emission_1.value + emission_2.value
    start_date = min(emission_1.start_date, emission_2.start_date)
    end_date = max(emission_1.end_date, emission_2.end_date)

    methods = [
        method for emission in (emission_1, emission_2)
        if isinstance((method := emission.method), EmissionMethodTier)
    ]

    method = min_emission_method_tier(*methods) if methods else None

    return CarbonStockChangeEmission(value, start_date, end_date, method)


def create_should_run_function(
    *,
    carbon_stock_term_id: str,
    get_valid_management_nodes_func: Callable[[dict], list[dict]],
    should_compile_inventory_func: Callable[[dict, list[dict], list[dict]], tuple[bool, dict]],
    summarise_land_use_func: Callable[[list[dict]], Any],
    detect_land_use_change_func: Callable[[Any, Any], bool],
    should_run_measurement_func: Callable[[dict], bool] = lambda *_: True,
    measurement_method_ranking: list[MeasurementMethodClassification] = DEFAULT_MEASUREMENT_METHOD_RANKING
) -> Callable[[dict], tuple[bool, str, dict, dict]]:
    """
    Create a should run function for an emissions from carbon stock change model.

    Model-specific validation functions should be passed as parameters to this higher order function to determine which
    carbon stock measurements are included in the inventory and whether there is enough data to compile an annual
    inventory of carbon stock change data.

    Parameters
    ----------
    carbon_stock_term_id : str
        The `term.@id` of the carbon stock measurement (e.g., `aboveGroundBiomass`, `belowGroundBiomass`,
        `organicCarbonPerHa`, etc.).

    should_compile_inventory_func : Callable[[dict, list[dict], list[dict]], tuple[bool, dict]]
        A function, with the signature
        `(site: dict, cycles: list[dict], carbon_stock_measurements: list[dict]) -> (should_run: bool, logs: dict)`, to
        determine whether there is enough site and cycles data available to compile the carbon stock change inventory.

    get_valid_management_nodes_func : Callable[[dict], list[dict]]
        A function, with the signature... `(site: dict) -> management_nodes: list[dict]` to extract valid management
        nodes from the site for building the land use inventory.

    summarise_land_use_func: Callable[[list[dict]], Any]
        A function with the signature `(nodes: list[dict]) -> Any`, to reduce a list of `landCover`
        [Management](https://www.hestia.earth/schema/Management) nodes into a land use summary that can be compared
        with other summaries to determine whether land use change events have occured.

    detect_land_use_change_func: Callable[[Any, Any], bool]
        A function with the signature `(summary_a: Any, summary_b: Any) -> bool`, to determine whether a land use
        change event has occured.

    should_run_measurement_func : Callable[[dict], bool], optional.
        An optional measurement validation function, with the signature `(measurement: dict) -> bool`, that can be used
        to add in additional criteria (`depthUpper`, `depthLower`, etc.) for the inclusion of a measurement in the
        inventory.

    measurement_method_ranking : list[MeasurementMethodClassification], optional
        The order in which to prioritise `MeasurementMethodClassification`s when reducing the inventory down to a
        single method per year. Defaults to:
        ```
        MeasurementMethodClassification.ON_SITE_PHYSICAL_MEASUREMENT,
        MeasurementMethodClassification.MODELLED_USING_OTHER_MEASUREMENTS,
        MeasurementMethodClassification.TIER_3_MODEL,
        MeasurementMethodClassification.TIER_2_MODEL,
        MeasurementMethodClassification.TIER_1_MODEL
        ```
        n.b., measurements with methods not included in the ranking will not be included in the inventory.

    Returns
    -------
    Callable[[dict], tuple[bool, str, dict, dict]]
        The customised `should_run` function with the signature
        `(cycle: dict) -> (should_run_: bool, cycle_id: str, inventory: dict, logs: dict)`.
    """

    def should_run(cycle: dict) -> tuple[bool, str, dict, dict]:
        """
        Determine if calculations should run for a given [Cycle](https://www.hestia.earth/schema/Cycle) based on
        available carbon stock data. If data availability is sufficient, return an inventory of pre-processed input
        data for the model and log data.

        Parameters
        ----------
        cycle : dict
            The cycle dictionary for which the calculations will be evaluated.

        Returns
        -------
        tuple[bool, str, dict, dict]
            `(should_run, cycle_id, inventory, logs)`
        """
        cycle_id = cycle.get("@id")
        cycle_start_date = cycle.get("startDate")
        cycle_end_date = cycle.get("endDate")

        site = _get_site(cycle)
        cycles = related_cycles(site, cycles_mapping={cycle_id: cycle})

        carbon_stock_measurements = [
            node for node in site.get("measurements", [])
            if all([
                node_term_match(node, carbon_stock_term_id),
                _has_valid_array_fields(node),
                _has_valid_dates(node),
                node.get("methodClassification") in (m.value for m in measurement_method_ranking),
                should_run_measurement_func(node)
            ])
        ]

        land_cover_nodes = get_valid_management_nodes_func(site)

        seed = gen_seed(site, MODEL, carbon_stock_term_id)  # All cycles linked to the same site should be consistent
        rng = random.default_rng(seed)

        should_compile_inventory, should_compile_logs = should_compile_inventory_func(
            site, cycles, carbon_stock_measurements
        )

        compile_inventory_func = _create_compile_inventory_function(
            summarise_land_use_func=summarise_land_use_func,
            detect_land_use_change_func=detect_land_use_change_func,
            iterations=_ITERATIONS,
            seed=rng,
            measurement_method_ranking=measurement_method_ranking
        )

        inventory, inventory_logs = (
            compile_inventory_func(
                cycles,
                carbon_stock_measurements,
                land_cover_nodes
            ) if should_compile_inventory else ({}, {})
        )

        has_valid_inventory = len(inventory) > 0
        has_consecutive_years = check_consecutive(inventory.keys())

        should_run_ = all([has_valid_inventory, has_consecutive_years])

        kwargs = {
            "cycle_id": cycle_id,
            "cycle_start_date": cycle_start_date,
            "cycle_end_date": cycle_end_date,
            "inventory": inventory
        }

        logs = should_compile_logs | inventory_logs | {
            "seed": seed,
            "has_valid_inventory": has_valid_inventory,
            "has_consecutive_years": has_consecutive_years,
            "has_stock_measurements": bool(carbon_stock_measurements)
        }

        return should_run_, kwargs, logs

    return should_run


def _has_valid_array_fields(node: dict) -> bool:
    """Validate that the array-type fields of a node (`value`, `dates`, `sd`) have data and matching lengths."""
    value = node.get("value", [])
    sd = node.get("sd", [])
    dates = node.get("dates", [])
    return all([
        len(value) > 0,
        len(value) == len(dates),
        len(sd) == 0 or len(sd) == len(value)
    ])


def _has_valid_dates(node: dict) -> bool:
    """Validate that all dates in a node's `dates` field have a valid format."""
    return all(_get_datestr_format(datestr) in _VALID_DATE_FORMATS for datestr in node.get("dates", []))


def _get_site(cycle: dict) -> dict:
    """
    Get the [Site](https://www.hestia.earth/schema/Site) data from a [Cycle](https://www.hestia.earth/schema/Cycle).

    Parameters
    ----------
    cycle : dict

    Returns
    -------
    str
    """
    return cycle.get("site", {})


def _create_compile_inventory_function(
    *,
    summarise_land_use_func: Callable[[list[dict]], Any],
    detect_land_use_change_func: Callable[[Any, Any], bool],
    iterations: int = 10000,
    seed: Union[int, random.Generator, None] = None,
    measurement_method_ranking: list[MeasurementMethodClassification] = DEFAULT_MEASUREMENT_METHOD_RANKING
) -> Callable:
    """
    Create a compile inventory function for an emissions from carbon stock change model.

    Model-specific validation functions should be passed as parameters to this higher order function to determine how
    land cover data is reduced down to a land use summary and how those land use summaries should be compared to
    determine when land use change events have occured.

    Parameters
    ----------
    summarise_land_use_func: Callable[[list[dict]], Any]
        A function with the signature `(nodes: list[dict]) -> Any`, to reduce a list of `landCover`
        [Management](https://www.hestia.earth/schema/Management) nodes into a land use summary that can be compared
        with other summaries to determine whether land use change events have occured.

    detect_land_use_change_func: Callable[[Any, Any], bool]
        A function with the signature `(summary_a: Any, summary_b: Any) -> bool`, to determine whether a land use
        change event has occured.

    iterations : int, optional
        The number of iterations for stochastic processing (default is 10,000).

    seed : int, random.Generator, or None, optional
        Seed for random number generation to ensure reproducibility. Default is None.

    measurement_method_ranking : list[MeasurementMethodClassification], optional
        The order in which to prioritise `MeasurementMethodClassification`s when reducing the inventory down to a
        single method per year. Defaults to:
        ```
        MeasurementMethodClassification.ON_SITE_PHYSICAL_MEASUREMENT,
        MeasurementMethodClassification.MODELLED_USING_OTHER_MEASUREMENTS,
        MeasurementMethodClassification.TIER_3_MODEL,
        MeasurementMethodClassification.TIER_2_MODEL,
        MeasurementMethodClassification.TIER_1_MODEL
        ```
        n.b., measurements with methods not included in the ranking will not be included in the inventory.

    Returns
    ----------
    Callable
        The `compile_inventory` function.
    """
    def compile_inventory(
        cycles: list[dict],
        carbon_stock_measurements: list[dict],
        land_cover_nodes: list[dict]
    ) -> tuple[dict, dict]:
        """
        Compile an annual inventory of carbon stocks, changes in carbon stocks, carbon stock change emissions, and the
        share of emissions of cycles based on the provided cycles and measurement data.

        A separate inventory is compiled for each valid `MeasurementMethodClassification` present in the data, and the
        strongest available method is chosen for each relevant inventory year. These inventories are then merged into
        one final result.

        The final inventory structure is:
        ```
        {
            year (int): {
                _InventoryKey.CARBON_STOCK: value (CarbonStock),
                _InventoryKey.CARBON_STOCK_CHANGE: value (CarbonStockChange),
                _InventoryKey.CO2_EMISSION: value (CarbonStockChangeEmission),
                _InventoryKey.SHARE_OF_EMISSION: {
                    cycle_id (str): value (float),
                    ...cycle_ids
                },
                _InventoryKey.YEARS_SINCE_LUC_EVENT: value (int)
            },
            ...years
        }
        ```

        Parameters
        ----------
        cycle_id : str
            The unique identifier of the cycle being processed.
        cycles : list[dict]
            A list of [Cycle](https://www.hestia.earth/schema/Cycles) nodes related to the site.
        carbon_stock_measurements : list[dict]
            A list of [Measurement](https://www.hestia.earth/schema/Measurement) nodes, representing carbon stock
            measurements across time and methods.
        land_cover_nodes : list[dict]
            A list of `landCover `[Management](https://www.hestia.earth/schema/Management) nodes, representing the
            site's land cover over time.


        Returns
        -------
        tuple[dict, dict]
            `(inventory, logs)`
        """
        cycle_inventory = _compile_cycle_inventory(cycles)
        carbon_stock_inventory = _compile_carbon_stock_inventory(
            carbon_stock_measurements, iterations=iterations, seed=seed
        )
        land_use_inventory = _compile_land_use_inventory(
            land_cover_nodes, summarise_land_use_func, detect_land_use_change_func
        )

        inventory = _squash_inventory(
            cycle_inventory,
            carbon_stock_inventory,
            land_use_inventory,
            measurement_method_ranking=measurement_method_ranking
        )

        logs = _generate_logs(cycle_inventory, carbon_stock_inventory, land_use_inventory)

        return inventory, logs

    return compile_inventory


def _compile_cycle_inventory(cycles: list[dict]) -> dict:
    """
    Calculate grouped share of emissions for cycles based on the amount they contribute the the overall land management
    of an inventory year.

    This function groups cycles by year, then calculates the share of emissions for each cycle based on the
    `fraction_of_group_duration` value. The share of emissions is normalized by the sum of cycle occupancies for the
    entire dataset to ensure the values represent a valid share.

    The returned inventory has the shape:
    ```
    {
        year (int): {
            _InventoryKey.SHARE_OF_EMISSION: {
                cycle_id (str): value (float),
                ...cycle_ids
            }
        },
        ...more years
    }
    ```

    Parameters
    ----------
    cycles : list[dict]
        List of [Cycle nodes](https://www.hestia.earth/schema/Cycle), where each cycle dictionary should contain a
        "fraction_of_group_duration" key added by the `group_nodes_by_year` function.
    iterations : int, optional
        Number of iterations for stochastic sampling when processing carbon stock values (default is 10,000).
    seed : int, random.Generator, or None, optional
        Seed for random number generation (default is None).

    Returns
    -------
    dict
        A dictionary with grouped share of emissions for each cycle based on the fraction of the year.
    """
    grouped_cycles = group_nodes_by_year(cycles)

    def calculate_emissions(cycles_in_year):
        total_fraction = sum(c.get("fraction_of_group_duration", 0) for c in cycles_in_year)
        return {
            cycle["@id"]: cycle.get("fraction_of_group_duration", 0) / total_fraction
            for cycle in cycles_in_year
        }

    return {
        year: {_InventoryKey.SHARE_OF_EMISSION: calculate_emissions(cycles_in_year)}
        for year, cycles_in_year in grouped_cycles.items()
    }


def _compile_carbon_stock_inventory(
    carbon_stock_measurements: list[dict],
    iterations: int = 10000,
    seed: Union[int, random.Generator, None] = None
) -> dict:
    """
    Compile an annual inventory of carbon stock data and pre-computed carbon stock change emissions.

    Carbon stock measurements are grouped by the method used (MeasurementMethodClassification). For each method,
    carbon stocks are processed for each year and changes between years are computed, followed by the calculation of
    CO2 emissions.

    The returned inventory has the shape:
    ```
    {
        method (MeasurementMethodClassification): {
            year (int): {
                _InventoryKey.CARBON_STOCK: value (CarbonStock),
                _InventoryKey.CARBON_STOCK_CHANGE: value (CarbonStockChange),
                _InventoryKey.CO2_EMISSION: value (CarbonStockChangeEmission)
            },
            ...more years
        }
        ...more methods
    }
    ```

    Parameters
    ----------
    carbon_stock_measurements : list[dict]
        List of carbon [Measurement nodes](https://www.hestia.earth/schema/Measurement) nodes.
    iterations : int, optional
        Number of iterations for stochastic sampling when processing carbon stock values (default is 10,000).
    seed : int, random.Generator, or None, optional
        Seed for random number generation (default is None).

    Returns
    -------
    dict
        The carbon stock inventory grouped by measurement method classification.
    """
    carbon_stock_measurements_by_method = group_measurements_by_method_classification(carbon_stock_measurements)

    return {
        method: _process_carbon_stock_measurements(measurements, iterations=iterations, seed=seed)
        for method, measurements in carbon_stock_measurements_by_method.items()
    }


def _process_carbon_stock_measurements(
    carbon_stock_measurements: list[dict],
    iterations: int = 10000,
    seed: Union[int, random.Generator, None] = None
) -> dict:
    """
    Process carbon stock measurements to compile an annual inventory of carbon stocks, carbon stock changes, and CO2
    emissions. The inventory is built by interpolating between measured values and calculating changes across years.

    The returned inventory has the shape:
    ```
    {
        year (int): {
            _InventoryKey.CARBON_STOCK: value (CarbonStock),
            _InventoryKey.CARBON_STOCK_CHANGE: value (CarbonStockChange),
            _InventoryKey.CO2_EMISSION: value (CarbonStockChangeEmission)
        },
        ...more years
    }
    ```

    Parameters
    ----------
    carbon_stock_measurements : list[dict]
        List of pre-validated carbon stock [Measurement nodes](https://www.hestia.earth/schema/Measurement).
    iterations : int, optional
        Number of iterations for stochastic sampling when processing carbon stock values (default is 10,000).
    seed : int, random.Generator, or None, optional
        Seed for random number generation (default is None).

    Returns
    -------
    dict
        The annual inventory.
    """
    carbon_stocks = _preprocess_carbon_stocks(carbon_stock_measurements, iterations, seed)

    carbon_stocks_by_year = _interpolate_carbon_stocks(carbon_stocks)
    carbon_stock_changes_by_year = _calculate_stock_changes(carbon_stocks_by_year)
    co2_emissions_by_year = _calculate_co2_emissions(carbon_stock_changes_by_year)

    return _sorted_merge(carbon_stocks_by_year, carbon_stock_changes_by_year, co2_emissions_by_year)


def _preprocess_carbon_stocks(
    carbon_stock_measurements: list[dict],
    iterations: int = 10000,
    seed: Union[int, random.Generator, None] = None
) -> list[CarbonStock]:
    """
    Pre-process a list of carbon stock measurements by normalizing and sorting them by date. The measurements are used
    to create correlated samples using stochastic sampling methods.

    The carbon stock measurements are processed to fill in any gaps in data (e.g., missing standard deviations), and
    correlated samples are drawn to handle measurement uncertainty.

    Parameters
    ----------
    carbon_stock_measurements : list[dict]
        List of pre-validated carbon stock [Measurement nodes](https://www.hestia.earth/schema/Measurement).
    iterations : int, optional
        Number of iterations for stochastic sampling when processing carbon stock values (default is 10,000).
    seed : int, random.Generator, or None, optional
        Seed for random number generation (default is None).

    Returns
    -------
    list[CarbonStock]
        A list of carbon stocks sorted by date.
    """
    dates, values, sds, methods = _extract_node_data(
        flatten([split_node_by_dates(m) for m in carbon_stock_measurements])
    )

    correlation_matrix = compute_time_series_correlation_matrix(
        dates,
        decay_fn=lambda dt: exponential_decay(
            dt,
            tau=calc_tau(_TRANSITION_PERIOD_DAYS),
            initial_value=_MAX_CORRELATION,
            final_value=_MIN_CORRELATION
        )
    )

    correlated_samples = correlated_normal_2d(
        iterations,
        array(values),
        array(sds),
        correlation_matrix,
        seed=seed
    )

    return [
        CarbonStock(value=sample, date=date, method=method)
        for sample, date, method in zip(correlated_samples, dates, methods)
    ]


def _extract_node_data(nodes: list[dict]) -> list[dict]:

    def group_node(result, node) -> dict[str, dict]:
        date = _gapfill_datestr(node["dates"][0], DatestrGapfillMode.END)
        result[date] = result.get(date, []) + [node]
        return result

    grouped_nodes = reduce(group_node, nodes, dict())

    def get_values(date):
        return flatten(node.get("value", []) for node in grouped_nodes[date])

    def get_sds(date):
        return flatten(
            node.get("sd", []) or [_calc_nominal_sd(v, _NOMINAL_ERROR) for v in node.get("value", [])]
            for node in grouped_nodes[date]
        )

    def get_methods(date):
        return flatten(node.get("methodClassification", []) for node in grouped_nodes[date])

    dates = sorted(grouped_nodes.keys())
    values = [mean(get_values(date)) for date in dates]
    sds = [mean(get_sds(date)) for date in dates]
    methods = [min_measurement_method_classification(get_methods(date)) for date in dates]

    return dates, values, sds, methods


def _calc_nominal_sd(value: float, error: float) -> float:
    """
    Calculate a nominal SD for a carbon stock measurement. Can be used to gap fill SD when information not present in
    measurement node.
    """
    return value * error / 200


def _interpolate_carbon_stocks(carbon_stocks: list[CarbonStock]) -> dict:
    """
    Interpolate between carbon stock measurements to estimate annual carbon stocks.

    The function takes a list of carbon stock measurements and interpolates between pairs of consecutive measurements
    to estimate the carbon stock values for each year in between.

    The returned dictionary has the format:
    ```
    {
        year (int): {
            _InventoryKey.CARBON_STOCK: value (CarbonStock),
        },
        ...more years
    }
    ```
    """
    def interpolate_between(result: dict, carbon_stock_pair: tuple[CarbonStock, CarbonStock]) -> dict:
        start, end = carbon_stock_pair[0], carbon_stock_pair[1]

        start_date = safe_parse_date(start.date, datetime.min)
        end_date = safe_parse_date(end.date, datetime.min)

        should_run = (
            datetime.min != start_date != end_date
            and end_date > start_date
        )

        update = {
            year: {_InventoryKey.CARBON_STOCK: _lerp_carbon_stocks(
                start,
                end,
                f"{year}-12-31T23:59:59"
            )} for year in range(start_date.year, end_date.year+1)
        } if should_run else {}

        return result | update

    return reduce(interpolate_between, pairwise(carbon_stocks), dict())


def _calculate_stock_changes(carbon_stocks_by_year: dict) -> dict:
    """
    Calculate the change in carbon stock between consecutive years.

    The function takes a dictionary of carbon stock values keyed by year and computes the difference between the
    carbon stock for each year and the previous year. The result is stored as a `CarbonStockChange` object.

    The returned dictionary has the format:
    ```
    {
        year (int): {
            _InventoryKey.CARBON_STOCK_CHANGE: value (CarbonStockChange),
        },
        ...more years
    }
    ```
    """
    return {
        year: {
            _InventoryKey.CARBON_STOCK_CHANGE: _calc_carbon_stock_change(
                start_group[_InventoryKey.CARBON_STOCK],
                end_group[_InventoryKey.CARBON_STOCK]
            )
        } for (_, start_group), (year, end_group) in pairwise(carbon_stocks_by_year.items())
    }


def _calculate_co2_emissions(carbon_stock_changes_by_year: dict) -> dict:
    """
    Calculate CO2 emissions from changes in carbon stock between consecutive years.

    The function takes a dictionary of carbon stock changes and calculates the corresponding CO2 emissions for each
    year using a predefined emission factor.

    The returned dictionary has the format:
    ```
    {
        year (int): {
            _InventoryKey.CO2_EMISSION: value (CarbonStockChangeEmission),
        },
        ...more years
    }
    ```
    """
    return {
        year: {
            _InventoryKey.CO2_EMISSION: _calc_carbon_stock_change_emission(
                group[_InventoryKey.CARBON_STOCK_CHANGE]
            )
        } for year, group in carbon_stock_changes_by_year.items()
    }


def _compile_land_use_inventory(
    land_cover_nodes: list[dict],
    summarise_land_use_func: Callable[[list[dict]], Any],
    detect_land_use_change_func: Callable[[Any, Any], bool]
) -> dict:
    """
    Compile an annual inventory of land use data.

    The returned inventory has the shape:
    ```
    {
        year (int): {
            _InventoryKey.LAND_USE_SUMMARY: value (Any),
            _InventoryKey.LAND_USE_CHANGE_EVENT: value (bool),
            _InventoryKey.YEARS_SINCE_LUC_EVENT: value (int)
        },
        ...years
    }
    ```

    Parameters
    ----------
    land_cover_nodes : list[dict]
        A list of `landCover` Management nodes, representing the site's land cover over time.
    summarise_land_use_func: Callable[[list[dict]], Any]
        A function with the signature `(nodes: list[dict]) -> Any`, to reduce a list of `landCover` Management nodes
        into a land use summary that can be compared with other summaries to determine whether land use change events
        have occured.
    detect_land_use_change_func: Callable[[Any, Any], bool]
        A function with the signature `(summary_a: Any, summary_b: Any) -> bool`, to determine whether a land use
        change event has occured.

    Returns
    -------
    dict
        The land use inventory.
    """
    land_cover_nodes_by_year = group_nodes_by_year(land_cover_nodes)

    def build_inventory_year(result: dict, year_pair: tuple[int, int]) -> dict:
        """
        Build a year of the inventory using the data from `land_cover_nodes_by_year`.

        Parameters
        ----------
        inventory: dict
            The land cover change portion of the inventory. Must have the same shape as the returned dict.
        year_pair : tuple[int, int]
            A tuple with the shape `(prev_year, current_year)`.
        Returns
        -------
        dict
            The land use inventory.
        """

        prev_year, current_year = year_pair
        land_cover_nodes = land_cover_nodes_by_year.get(current_year, {})

        land_use_summary = summarise_land_use_func(land_cover_nodes)
        prev_land_use_summary = result.get(prev_year, {}).get(_InventoryKey.LAND_USE_SUMMARY, {})

        is_luc_event = detect_land_use_change_func(land_use_summary, prev_land_use_summary)

        time_delta = current_year - prev_year
        prev_years_since_luc_event = (
            result.get(prev_year, {}).get(_InventoryKey.YEARS_SINCE_LUC_EVENT, _TRANSITION_PERIOD_YEARS)
        )
        prev_years_since_inventory_start = result.get(prev_year, {}).get(_InventoryKey.YEARS_SINCE_INVENTORY_START, 0)

        years_since_luc_event = time_delta if is_luc_event else prev_years_since_luc_event + time_delta
        years_since_inventory_start = prev_years_since_inventory_start + time_delta

        update_dict = {
            current_year: {
                _InventoryKey.LAND_USE_SUMMARY: land_use_summary,
                _InventoryKey.LAND_USE_CHANGE_EVENT: is_luc_event,
                _InventoryKey.YEARS_SINCE_LUC_EVENT: years_since_luc_event,
                _InventoryKey.YEARS_SINCE_INVENTORY_START: years_since_inventory_start
            }
        }
        return result | update_dict

    should_run = len(land_cover_nodes_by_year) > 0
    start_year = min(land_cover_nodes_by_year.keys(), default=None)

    return reduce(
        build_inventory_year,
        pairwise(land_cover_nodes_by_year.keys()),  # Inventory years need data from previous year to be compiled.
        {
            start_year: {
                _InventoryKey.LAND_USE_SUMMARY: summarise_land_use_func(
                    land_cover_nodes_by_year.get(start_year, [])
                )
            }
        }
    ) if should_run else {}


def _sorted_merge(*sources: Union[dict, list[dict]]) -> dict:
    """
    Merge one or more dictionaries into a single dictionary, ensuring that the keys are sorted in temporal order.

    Parameters
    ----------
    *sources : dict | list[dict]
        One or more dictionaries or lists of dictionaries to be merged.

    Returns
    -------
    dict
        A new dictionary containing the merged key-value pairs, with keys sorted.
    """

    _sources = non_empty_list(
        flatten([arg if isinstance(arg, list) else [arg] for arg in sources])
    )

    merged = reduce(merge, _sources, {})
    return dict(sorted(merged.items()))


def _squash_inventory(
    cycle_inventory: dict,
    carbon_stock_inventory: dict,
    land_use_inventory: dict,
    measurement_method_ranking: list[MeasurementMethodClassification] = DEFAULT_MEASUREMENT_METHOD_RANKING
) -> dict:
    """
    Combine the `cycle_inventory` and `carbon_stock_inventory` into a single inventory by merging data for each year
    using the strongest available `MeasurementMethodClassification`. Any years not relevant to the cycle identified
    by `cycle_id` are excluded.

    Parameters
    ----------

    cycle_inventory : dict
        A dictionary representing the share of emissions for each cycle, grouped by year.
        Format:
        ```
        {
            year (int): {
                _InventoryKey.SHARE_OF_EMISSION: {
                    cycle_id (str): value (float),
                    ...other cycle_ids
                }
            },
            ...more years
        }
        ```

    carbon_stock_inventory : dict
        A dictionary representing carbon stock and emissions data grouped by measurement method and year.
        Format:
        ```
        {
            method (MeasurementMethodClassification): {
                year (int): {
                    _InventoryKey.CARBON_STOCK: value (CarbonStock),
                    _InventoryKey.CARBON_STOCK_CHANGE: value (CarbonStockChange),
                    _InventoryKey.CO2_EMISSION: value (CarbonStockChangeEmission)
                },
                ...more years
            },
            ...more methods
        }
        ```

    land_use_inventory : dict
        A dictionary representing land use and land use change data grouped by year.
        Format:
        ```
        {
            year (int): {
                _InventoryKey.LAND_USE_SUMMARY: value (Any),
                _InventoryKey.LAND_USE_CHANGE_EVENT: value (bool),
                _InventoryKey.YEARS_SINCE_LUC_EVENT: value (int)
            },
            ...years
        }
        ```

    measurement_method_ranking : list[MeasurementMethodClassification], optional
        The order in which to prioritise `MeasurementMethodClassification`s when reducing the inventory down to a
        single method per year. Defaults to:
        ```
        MeasurementMethodClassification.ON_SITE_PHYSICAL_MEASUREMENT,
        MeasurementMethodClassification.MODELLED_USING_OTHER_MEASUREMENTS,
        MeasurementMethodClassification.TIER_3_MODEL,
        MeasurementMethodClassification.TIER_2_MODEL,
        MeasurementMethodClassification.TIER_1_MODEL
        ```
        n.b., measurements with methods not included in the ranking will not be included in the inventory.

    Returns
    -------
    dict
        A combined inventory that merges cycle and carbon stock inventories for relevant years and cycles.
        The resulting structure is:
        ```
        {
            year (int): {
                _InventoryKey.CARBON_STOCK: value (CarbonStock),
                _InventoryKey.CARBON_STOCK_CHANGE: value (CarbonStockChange),
                _InventoryKey.CO2_EMISSION: value (CarbonStockChangeEmission),
                _InventoryKey.SHARE_OF_EMISSION: {
                    cycle_id (str): value (float),
                    ...other cycle_ids
                }
            },
            ...more years
        }
        ```
    """
    inventory_years = sorted(set(non_empty_list(
        flatten(list(years) for years in carbon_stock_inventory.values())
        + list(cycle_inventory.keys())
    )))

    def should_run_group(method: MeasurementMethodClassification, year: int) -> bool:
        return _InventoryKey.CO2_EMISSION in carbon_stock_inventory.get(method, {}).get(year, {}).keys()

    def squash(result: dict, year: int) -> dict:
        method = next(
            (method for method in measurement_method_ranking if should_run_group(method, year)),
            None
        )
        update_dict = {
            year: {
                **_get_land_use_change_data(year, land_use_inventory),
                **reduce(merge, [
                    carbon_stock_inventory.get(method, {}).get(year, {}),
                    cycle_inventory.get(year, {})
                ], dict())
            }
        }
        return result | update_dict

    return reduce(squash, inventory_years, dict())


def _get_land_use_change_data(
    year: int,
    land_use_inventory: dict
) -> dict:
    """
    Retrieve a value for `_InventoryKey.YEARS_SINCE_LUC_EVENT` for a specific inventory year, or gapfill it from
    available data.

    If no land use data is available in the inventory, the site is assumed to have a stable land use and all emissions
    will be allocated to management changes.
    """
    closest_inventory_year = next(
        (key for key in land_use_inventory.keys() if key >= year),      # get the next inventory year
        min(
            land_use_inventory.keys(), key=lambda x: abs(x - year),     # else the previous
            default=None                                                # else return `None`
        )
    )

    time_delta = closest_inventory_year - year if closest_inventory_year else 0
    prev_years_since_luc_event = (
        land_use_inventory.get(closest_inventory_year, {}).get(_InventoryKey.YEARS_SINCE_LUC_EVENT)
    )
    prev_years_since_inventory_start = (
        land_use_inventory.get(closest_inventory_year, {}).get(_InventoryKey.YEARS_SINCE_INVENTORY_START)
    )

    years_since_luc_event = prev_years_since_luc_event - time_delta if prev_years_since_luc_event else None
    years_since_inventory_start = (
        prev_years_since_inventory_start - time_delta if prev_years_since_inventory_start else None
    )

    return {
        _InventoryKey.YEARS_SINCE_LUC_EVENT: years_since_luc_event,
        _InventoryKey.YEARS_SINCE_INVENTORY_START: years_since_inventory_start
    }


def _generate_logs(
    cycle_inventory: dict,
    carbon_stock_inventory: dict,
    land_use_inventory: dict
) -> dict:
    """
    Generate logs for the compiled inventory, providing details about cycle, carbon and land use inventories.

    Parameters
    ----------
    cycle_inventory : dict
        The compiled cycle inventory.
    carbon_stock_inventory : dict
        The compiled carbon stock inventory.
    land_use_inventory : dict
        The compiled carbon stock inventory.

    Returns
    -------
    dict
        A dictionary containing formatted log entries for cycle and carbon inventories.
    """
    logs = {
        "cycle_inventory": _format_cycle_inventory(cycle_inventory),
        "carbon_stock_inventory": _format_carbon_stock_inventory(carbon_stock_inventory),
        "land_use_inventory": _format_land_use_inventory(land_use_inventory)
    }
    return logs


def _format_cycle_inventory(cycle_inventory: dict) -> str:
    """
    Format the cycle inventory for logging as a table. Rows represent inventory years, columns represent the share of
    emission for each cycle present in the inventory. If the inventory is invalid, return `"None"` as a string.
    """
    KEY = _InventoryKey.SHARE_OF_EMISSION

    unique_cycles = sorted(
        set(non_empty_list(flatten(list(group[KEY]) for group in cycle_inventory.values()))),
        key=lambda id: next((year, id) for year in cycle_inventory if id in cycle_inventory[year][KEY])
    )

    should_run = cycle_inventory and len(unique_cycles) > 0

    return log_as_table(
        {
            "year": year,
            **{
                id: _format_number(group.get(KEY, {}).get(id, 0)) for id in unique_cycles
            }
        } for year, group in cycle_inventory.items()
    ) if should_run else "None"


def _format_carbon_stock_inventory(carbon_stock_inventory: dict) -> str:
    """
    Format the carbon stock inventory for logging as a table. Rows represent inventory years, columns represent carbon
    stock change data for each measurement method classification present in inventory. If the inventory is invalid,
    return `"None"` as a string.
    """
    KEYS = [
        _InventoryKey.CARBON_STOCK,
        _InventoryKey.CARBON_STOCK_CHANGE,
        _InventoryKey.CO2_EMISSION
    ]

    methods = carbon_stock_inventory.keys()
    method_columns = list(product(methods, KEYS))
    inventory_years = sorted(set(non_empty_list(flatten(list(years) for years in carbon_stock_inventory.values()))))

    should_run = carbon_stock_inventory and len(inventory_years) > 0

    return log_as_table(
        {
            "year": year,
            **{
                _format_column_header(method, key): _format_named_tuple(
                    carbon_stock_inventory.get(method, {}).get(year, {}).get(key, {})
                ) for method, key in method_columns
            }
        } for year in inventory_years
    ) if should_run else "None"


def _format_land_use_inventory(land_use_inventory: dict) -> str:
    """
    Format the carbon stock inventory for logging as a table. Rows represent inventory years, columns represent land
    use change data. If the inventory is invalid, return `"None"` as a string.

    TODO: Implement logging of land use summary.
    """
    KEYS = [
        _InventoryKey.LAND_USE_CHANGE_EVENT,
        _InventoryKey.YEARS_SINCE_LUC_EVENT,
        _InventoryKey.YEARS_SINCE_INVENTORY_START
    ]

    inventory_years = sorted(set(non_empty_list(years for years in land_use_inventory.keys())))
    should_run = land_use_inventory and len(inventory_years) > 0

    return log_as_table(
        {
            "year": year,
            **{
                key.value: _LAND_USE_INVENTORY_KEY_TO_FORMAT_FUNC[key](
                    land_use_inventory.get(year, {}).get(key)
                ) for key in KEYS
            }
        } for year in inventory_years
    ) if should_run else "None"


def _format_bool(value: Optional[bool]) -> str:
    """Format a bool for logging in a table."""
    return str(value) if isinstance(value, bool) else "None"


def _format_int(value: Optional[float]) -> str:
    """Format an int for logging in a table. If the value is invalid, return `"None"` as a string."""
    return f"{value:.0f}" if isinstance(value, (float, int)) else "None"


def _format_number(value: Optional[float]) -> str:
    """Format a float for logging in a table. If the value is invalid, return `"None"` as a string."""
    return f"{value:.1f}" if isinstance(value, (float, int)) else "None"


def _format_column_header(method: MeasurementMethodClassification, inventory_key: _InventoryKey) -> str:
    """
    Format a measurement method classification and inventory key for logging in a table as a column header. Replace any
    whitespaces in the method value with dashes and concatenate it with the inventory key value, which already has the
    correct format.
    """
    return "-".join([
        method.value.replace(" ", "-"),
        inventory_key.value
    ])


def _format_named_tuple(value: Optional[Union[CarbonStock, CarbonStockChange, CarbonStockChangeEmission]]) -> str:
    """
    Format a named tuple (`CarbonStock`, `CarbonStockChange` or `CarbonStockChangeEmission`) for logging in a table.
    Extract and format just the value and discard the other data. If the value is invalid, return `"None"` as a string.
    """
    return (
        _format_number(mean(value.value))
        if isinstance(value, (CarbonStock, CarbonStockChange, CarbonStockChangeEmission))
        else "None"
    )


_LAND_USE_INVENTORY_KEY_TO_FORMAT_FUNC = {
    _InventoryKey.LAND_USE_CHANGE_EVENT: _format_bool,
    _InventoryKey.YEARS_SINCE_LUC_EVENT: _format_int,
    _InventoryKey.YEARS_SINCE_INVENTORY_START: _format_int
}
"""
Map inventory keys to format functions. The columns in inventory logged as a table will also be sorted in the order of
the `dict` keys.
"""


def create_run_function(
    new_emission_func: Callable[[EmissionMethodTier, dict], dict],
    land_use_change_emission_term_id: str,
    management_change_emission_term_id: str
) -> Callable[[str, dict], list[dict]]:
    """
    Create a run function for an emissions from carbon stock change model.

    A model-specific `new_emission_func` should be passed as a parameter to this higher-order function to control how
    model ouputs are formatted into HESTIA emission nodes.

    Parameters
    ----------
    new_emission_func : Callable[[EmissionMethodTier, tuple], dict]
        A function, with the signature `(method_tier: dict, **kwargs: dict) -> (emission_node: dict)`.
    land_use_change_emission_term_id : str
        The term id for emissions allocated to land use changes.
    management_change_emission_term_id : str
        The term id for emissions allocated to management changes.

    Returns
    -------
    Callable[[str, dict], list[dict]]
        The customised `run` function with the signature `(cycle_id: str, inventory: dict) -> emissions: list[dict]`.
    """
    def reduce_emissions(result: dict, year: int, cycle_id: str, inventory: dict):
        """
        Assign emissions to either the land use or management change term ids and sum together.
        """
        data = inventory[year]

        years_since_luc_event = data[_InventoryKey.YEARS_SINCE_LUC_EVENT]
        years_since_inventory_start = data[_InventoryKey.YEARS_SINCE_INVENTORY_START]
        share_of_emission = data[_InventoryKey.SHARE_OF_EMISSION][cycle_id]

        co2_emission = data.get(_InventoryKey.CO2_EMISSION)

        has_co2_emission = bool(co2_emission)
        is_luc_emission = bool(years_since_luc_event) and years_since_luc_event <= _TRANSITION_PERIOD_YEARS
        is_data_complete = bool(years_since_inventory_start) and years_since_inventory_start >= _TRANSITION_PERIOD_YEARS

        emission_term_id = (
            land_use_change_emission_term_id if is_luc_emission else management_change_emission_term_id
        ) if has_co2_emission else None

        zero_emission_term_id = (
            management_change_emission_term_id if is_luc_emission else
            (land_use_change_emission_term_id if is_data_complete else None)
        )

        rescaled_emission = _rescale_carbon_stock_change_emission(
            co2_emission, share_of_emission
        ) if emission_term_id else None

        zero_emission = get_zero_emission(year) if zero_emission_term_id else None

        previous_emission = result.get(emission_term_id)
        previous_zero_emission = result.get(zero_emission_term_id)

        emission_dict = {
            emission_term_id: (
                _add_carbon_stock_change_emissions(previous_emission, rescaled_emission) if previous_emission
                else rescaled_emission
            )
        } if emission_term_id else {}

        zero_emission_dict = {
            zero_emission_term_id: (
                _add_carbon_stock_change_emissions(previous_zero_emission, zero_emission) if previous_zero_emission
                else zero_emission
            )
        } if zero_emission_term_id else {}

        return result | emission_dict | zero_emission_dict

    def run(cycle_id: str, cycle_start_date: str, cycle_end_date: str, inventory: dict) -> list[dict]:
        """
        Calculate emissions for a specific cycle using from a carbon stock change using pre-compiled inventory data.

        The emission method tier is based on the minimum measurement method tier of the carbon stock measures used to
        calculate the emission.

        Parameters
        ----------
        cycle_id : str
            The "@id" field of the [Cycle node](https://www.hestia.earth/schema/Cycle).
        grouped_data : dict
            A dictionary containing grouped carbon stock change and share of emissions data.

        Returns
        -------
        list[dict]
            A list of [Emission](https://www.hestia.earth/schema/Emission) nodes containing model results.
        """

        def should_run_year(year: int) -> bool:
            return cycle_id in inventory.get(year, {}).get(_InventoryKey.SHARE_OF_EMISSION, {}).keys()

        assigned_emissions = reduce(
            lambda result, year: reduce_emissions(result, year, cycle_id, inventory),
            (year for year in inventory.keys() if should_run_year(year)),
            {}
        )

        return [
            new_emission_func(
                term_id=emission_term_id,
                method_tier=_get_emission_method(total_emission),
                **calc_descriptive_stats(
                    total_emission.value,
                    EmissionStatsDefinition.SIMULATED,
                    decimals=6
                )
            ) for emission_term_id, total_emission in assigned_emissions.items()
            if isinstance(total_emission, CarbonStockChangeEmission)
        ]

    return run


def get_zero_emission(year):
    return CarbonStockChangeEmission(
        value=array(0),
        start_date=_gapfill_datestr(year),
        end_date=_gapfill_datestr(year, DatestrGapfillMode.END),
        method=None
    )


def _get_emission_method(emission: CarbonStockChangeEmission):
    method = emission.method
    return method if isinstance(method, EmissionMethodTier) else EmissionMethodTier.TIER_1
