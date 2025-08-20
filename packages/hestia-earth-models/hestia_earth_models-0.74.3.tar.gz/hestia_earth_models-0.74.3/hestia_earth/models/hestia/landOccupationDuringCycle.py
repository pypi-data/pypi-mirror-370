from functools import reduce
from typing import NamedTuple

from hestia_earth.models.log import logRequirements, logShouldRun, log_as_table

from hestia_earth.models.utils import hectar_to_square_meter
from hestia_earth.models.utils.constant import DAYS_IN_YEAR
from hestia_earth.models.utils.indicator import _new_indicator
from hestia_earth.models.utils.impact_assessment import get_product
from hestia_earth.models.utils.site import get_land_cover_term_id as get_landCover_term_id_from_site_type
from hestia_earth.models.utils.crop import get_landCover_term_id
from hestia_earth.schema import CycleFunctionalUnit

from . import MODEL

REQUIREMENTS = {
    "ImpactAssessment": {
        "product": {
            "@type": "Term",
            "value": "> 0",
            "optional": {
                "@doc": "if the [cycle.functionalUnit](https://hestia.earth/schema/Cycle#functionalUnit) = 1 ha, additional properties are required",  # noqa: E501
                "economicValueShare": ">= 0"
            }
        },
        "cycle": {
            "@type": "Cycle",
            "site": {
                "@type": "Site",
                "country": {"@type": "Term", "termType": "region"}
            },
            "siteArea": "",
            "siteDuration": "",
            "siteUnusedDuration": "",
            "optional": {
                "@doc": "When `otherSites` are provided, `otherSitesArea`, `otherSitesDuration` and `otherSitesUnusedDuration` are required",  # noqa: E501
                "otherSites": [{
                    "@type": "Site",
                    "country": {"@type": "Term", "termType": "region"}
                }],
                "otherSitesArea": "",
                "otherSitesDuration": "",
                "otherSitesUnusedDuration": ""
            }
        }
    }
}
RETURNS = {
    "Indicator": [{
        "value": "",
        "landCover": ""
    }]
}
TERM_ID = 'landOccupationDuringCycle'


class SiteData(NamedTuple):
    id: str  # site.@id
    area: float
    duration: float
    unused_duration: float
    land_cover_id: str
    country_id: str


def _indicator(term_id: str, value: float, land_cover_id: str, country_id: str):
    indicator = _new_indicator(
        term_id, model=MODEL, land_cover_id=land_cover_id, country_id=country_id
    )
    indicator['value'] = round(value, 6)
    return indicator


def _calc_land_occupation_m2_per_ha(
    site_area: float, site_duration: float, site_unused_duration: float
) -> float:
    """
    Parameters
    ----------
    site_area : float
        Area of the site in hectares.
    site_duration : float
        Site duration in days.
    site_unused_duration : float
        Site unused duration in days.

    Returns
    -------
    float
    """
    return hectar_to_square_meter(site_area) * (site_duration + site_unused_duration) / DAYS_IN_YEAR


def _calc_land_occupation_m2_per_kg(
    yield_: float, economic_value_share: float, land_occupation_m2_per_ha: float,
) -> float:
    """
    Parameters
    ----------
    yield_ : float
        Product yield in product units.
    economic_value_share : float
        Economic value share of the product in % (0-100).
    land_occupation_m2_per_ha : float
        Land occupation in m2 ha-1.

    Returns
    -------
    float
    """
    return land_occupation_m2_per_ha * economic_value_share * 0.01 / yield_


_CYCLE_KEYS = (
    "site", "siteArea", "siteDuration", "siteUnusedDuration"
)

_CYCLE_KEY_MAPPING = {
    field: field.replace("site", "otherSites", 1) for field in _CYCLE_KEYS
}


def _build_inventory(cycle: dict, product: dict):
    product_land_cover_id = get_landCover_term_id(product.get("term", {}), skip_debug=True)

    cycle_data = {
        key: [value] + cycle.get(otherSites_key, []) for key, otherSites_key in _CYCLE_KEY_MAPPING.items()
        if (value := cycle.get(key))
    }

    n_sites = len(cycle_data.get("site", []))
    should_build_inventory = n_sites > 0 and all([
        len(cycle_data.get(key, [])) == n_sites for key in _CYCLE_KEYS[1:]
    ])

    inventory = [
        SiteData(
            id=site.get("@id"),
            area=cycle_data["siteArea"][i],
            duration=cycle_data["siteDuration"][i],
            unused_duration=cycle_data["siteUnusedDuration"][i],
            country_id=site.get("country", {}).get("@id"),
            land_cover_id=product_land_cover_id or get_landCover_term_id_from_site_type(site.get("siteType", {}))
        ) for i, site in enumerate(cycle_data.get("site", []))
    ] if should_build_inventory else []

    logs = {
        "n_sites": n_sites
    }

    return inventory, logs


def _should_run_site_data(site_data: SiteData) -> bool:
    return all([
        site_data.area >= 0,
        site_data.duration >= 0,
        site_data.unused_duration >= 0,
        site_data.land_cover_id,
        site_data.country_id
    ])


def _format_float(value: float, unit: str = "") -> str:
    return " ".join(
        string for string in [f"{value:.3g}", unit] if string
    ) if value else "None"


_INVALID_CHARS = {"_", ":", ",", "="}
_REPLACEMENT_CHAR = "-"


def _format_str(value: str) -> str:
    """Format a string for logging in a table. Remove all characters used to render the table on the front end."""
    return reduce(lambda x, char: x.replace(char, _REPLACEMENT_CHAR), _INVALID_CHARS, str(value))


def _format_inventory(inventory: list[SiteData]) -> str:
    return log_as_table(
        {
            "@id": _format_str(site_data.id),
            "site-area": _format_float(site_data.area, "ha"),
            "site-duration": _format_float(site_data.duration, "days"),
            "site-unused-duration": _format_float(site_data.unused_duration, "days"),
            "land-cover-id": _format_str(site_data.land_cover_id),
            "country-id": _format_str(site_data.country_id)
        } for site_data in inventory
    ) if inventory else "None"


def _should_run(impact_assessment: dict):

    cycle = impact_assessment.get("cycle")
    functional_unit = cycle.get("functionalUnit")

    product = get_product(impact_assessment)
    yield_ = sum(product.get("value", []))
    economic_value_share = (
        100 if functional_unit == CycleFunctionalUnit.RELATIVE.value
        else product.get("economicValueShare")
    )

    inventory, logs = _build_inventory(cycle, product)

    valid_inventory = inventory and all(_should_run_site_data(site_data) for site_data in inventory)

    logRequirements(
        impact_assessment,
        model=MODEL,
        term=TERM_ID,
        functional_unit=functional_unit,
        yield_=_format_float(yield_, product.get("term", {}).get("units")),
        economic_value_share=_format_float(economic_value_share, "pct"),
        site_inventory=_format_inventory(inventory),
        valid_inventory=valid_inventory,
        **logs
    )

    should_run = all([
        yield_ > 0,
        (
            economic_value_share is not None
            and economic_value_share >= 0
        ),
        valid_inventory
    ])

    logShouldRun(impact_assessment, MODEL, TERM_ID, should_run)

    return should_run, yield_, economic_value_share, inventory


def _run(
    yield_: float,
    economic_value_share: float,
    inventory: list[SiteData]
) -> list[dict]:

    def calc_occupation_by_group(result: dict, site_data: SiteData):
        """Calculate the land occupation of a site and sum it with matching landCover/country groups."""

        land_occupation_m2_per_ha = _calc_land_occupation_m2_per_ha(
            site_data.area, site_data.duration, site_data.unused_duration
        )

        land_occupation_m2_per_kg = _calc_land_occupation_m2_per_kg(
            yield_, economic_value_share, land_occupation_m2_per_ha
        )

        key = (site_data.land_cover_id, site_data.country_id)
        return result | {key: result.get(key, 0) + land_occupation_m2_per_kg}

    land_occupation_by_group = reduce(calc_occupation_by_group, inventory, {})

    return [
        _indicator(TERM_ID, value, land_cover_id, country_id)
        for (land_cover_id, country_id), value in land_occupation_by_group.items()
    ]


def run(impact_assessment: dict):
    should_run, yield_, economic_value_share, inventory = _should_run(impact_assessment)
    return _run(yield_, economic_value_share, inventory) if should_run else []
