from hestia_earth.schema import CycleFunctionalUnit, EmissionMethodTier, SiteSiteType

from hestia_earth.models.log import logRequirements, logShouldRun
from hestia_earth.models.utils.blank_node import cumulative_nodes_term_match
from hestia_earth.models.utils.emission import _new_emission

from .biomass_utils import detect_land_cover_change, get_valid_management_nodes, summarise_land_cover_nodes
from .co2ToAirCarbonStockChange_utils import create_run_function, create_should_run_function
from . import MODEL

REQUIREMENTS = {
    "Cycle": {
        "site": {
            "@type": "Site",
            "measurements": [
                {
                    "@type": "Measurement",
                    "value": "",
                    "dates": "",
                    "depthUpper": "0",
                    "depthLower": "30",
                    "term.@id": " belowGroundBiomass"
                }
            ]
        },
        "functionalUnit": "1 ha",
        "endDate": "",
        "optional": {
            "startDate": ""
        }
    }
}
RETURNS = {
    "Emission": [{
        "value": "",
        "sd": "",
        "min": "",
        "max": "",
        "statsDefinition": "simulated",
        "observations": "",
        "methodTier": "",
        "depth": 30
    }]
}
TERM_ID = 'co2ToAirBelowGroundBiomassStockChangeLandUseChange,co2ToAirBelowGroundBiomassStockChangeManagementChange'

_LU_EMISSION_TERM_ID = "co2ToAirBelowGroundBiomassStockChangeLandUseChange"
_MG_EMISSION_TERM_ID = "co2ToAirBelowGroundBiomassStockChangeManagementChange"

_DEPTH_UPPER = 0
_DEPTH_LOWER = 30

_CARBON_STOCK_TERM_ID = 'belowGroundBiomass'

_SITE_TYPE_SYSTEMS_MAPPING = {
    SiteSiteType.GLASS_OR_HIGH_ACCESSIBLE_COVER.value: [
        "protectedCroppingSystemSoilBased",
        "protectedCroppingSystemSoilAndSubstrateBased"
    ]
}


def _emission(
    *,
    term_id: str,
    value: list[float],
    method_tier: EmissionMethodTier,
    sd: list[float] = None,
    min: list[float] = None,
    max: list[float] = None,
    statsDefinition: str = None,
    observations: list[int] = None
) -> dict:
    """
    Create an emission node based on the provided value and method tier.

    See [Emission schema](https://www.hestia.earth/schema/Emission) for more information.

    Parameters
    ----------
    value : float
        The emission value (kg CO2 ha-1).
    sd : float
        The standard deviation (kg CO2 ha-1).
    method_tier : EmissionMethodTier
        The emission method tier.

    Returns
    -------
    dict
        The emission dictionary with keys 'depth', 'value', and 'methodTier'.
    """
    update_dict = {
        "value": value,
        "sd": sd,
        "min": min,
        "max": max,
        "statsDefinition": statsDefinition,
        "observations": observations,
        "methodTier": method_tier.value,
        "depth": _DEPTH_LOWER
    }
    emission = _new_emission(term_id, MODEL) | {
        key: value for key, value in update_dict.items() if value
    }
    return emission


def run(cycle: dict) -> list[dict]:
    """
    Run the `ipcc2019.co2ToAirBelowGroundBiomassStockChangeManagementChange`.

    Parameters
    ----------
    cycle : dict
        A HESTIA (Cycle node)[https://www.hestia.earth/schema/Cycle].

    Returns
    -------
    list[dict]
        A list of [Emission nodes](https://www.hestia.earth/schema/Emission) containing model results.
    """
    should_run_exec = create_should_run_function(
        carbon_stock_term_id=_CARBON_STOCK_TERM_ID,
        get_valid_management_nodes_func=get_valid_management_nodes,
        should_compile_inventory_func=_should_compile_inventory_func,
        summarise_land_use_func=summarise_land_cover_nodes,
        detect_land_use_change_func=detect_land_cover_change,
        should_run_measurement_func=_should_run_measurement_func
    )

    run_exec = create_run_function(
        new_emission_func=_emission,
        land_use_change_emission_term_id=_LU_EMISSION_TERM_ID,
        management_change_emission_term_id=_MG_EMISSION_TERM_ID
    )

    should_run, kwargs, logs = should_run_exec(cycle)

    for term_id in [_LU_EMISSION_TERM_ID, _MG_EMISSION_TERM_ID]:
        logRequirements(cycle, model=MODEL, term=term_id, **logs)
        logShouldRun(cycle, MODEL, term_id, should_run)

    return run_exec(**kwargs) if should_run else []


def _should_run_measurement_func(node: dict) -> bool:
    """
    Validate a [Measurement](https://www.hestia.earth/schema/Measurement) to determine whether it is a valid
    `organicCarbonPerHa` node.

    Parameters
    ----------
    node : dict
        The node to be validated.

    Returns
    -------
    bool
        `True` if the node passes all validation criteria, `False` otherwise.
    """
    return all([
        node.get("depthLower") == _DEPTH_LOWER,
        node.get("depthUpper") == _DEPTH_UPPER
    ])


def _should_compile_inventory_func(
    site: dict, cycles: list[dict], carbon_stock_measurements: list[dict]
) -> tuple[bool, dict]:
    """
    Determine whether a site is suitable and has enough data to compile a carbon stock inventory.

    Parameters
    ----------
    site : dict
        A HESTIA (Site node)[https://www.hestia.earth/schema/Site]
    cycles : list[dict]
        A list of HESTIA (Cycle nodes)[https://www.hestia.earth/schema/Cycle] that are related to the site.
    carbon_stock_measurements : list[dict]
        A list of HESTIA carbon stock (Measurement nodes)[https://www.hestia.earth/schema/Measurement] that are related
        to the site.

    Returns
    -------
    tuple[bool, dict]
        `(should_run, logs)`.
    """
    site_type = site.get("siteType")
    has_soil = site_type not in _SITE_TYPE_SYSTEMS_MAPPING or all(
        cumulative_nodes_term_match(
            cycle.get("practices", []),
            target_term_ids=_SITE_TYPE_SYSTEMS_MAPPING[site_type],
            cumulative_threshold=0
        ) for cycle in cycles
    )

    has_cycles = len(cycles) > 0
    has_functional_unit_1_ha = all(cycle.get('functionalUnit') == CycleFunctionalUnit._1_HA.value for cycle in cycles)

    should_run = all([
        has_soil,
        has_cycles,
        has_functional_unit_1_ha
    ])

    logs = {
        "site_type": site_type,
        "has_soil": has_soil,
        "carbon_stock_term": _CARBON_STOCK_TERM_ID,
        "has_cycles": has_cycles,
        "has_functional_unit_1_ha": has_functional_unit_1_ha,
    }

    return should_run, logs
