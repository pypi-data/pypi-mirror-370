from datetime import datetime
from dateutil.relativedelta import relativedelta
from hestia_earth.schema import TermTermType
from hestia_earth.utils.tools import to_precision

from hestia_earth.models.log import logRequirements, logShouldRun, debugValues
from hestia_earth.models.utils.blank_node import _gapfill_datestr, DatestrGapfillMode, DatestrFormat, _str_dates_match
from hestia_earth.models.utils.impact_assessment import get_site
from hestia_earth.models.utils.indicator import _new_indicator
from .utils import (
    LAND_USE_TERMS_FOR_TRANSFORMATION,
    crop_ipcc_land_use_category,
)
from . import MODEL

_MAXIMUM_OFFSET_DAYS = 365 * 2
_OUTPUT_SIGNIFICANT_DIGITS = 3
_RESOURCE_USE_TERM_ID = 'landOccupationDuringCycle'


def _new_indicator_with_value(
    term_id: str,
    land_cover_id: str,
    previous_land_cover_id: str,
    value: float
) -> dict:
    indicator = _new_indicator(
        term=term_id,
        model=MODEL,
        land_cover_id=land_cover_id,
        previous_land_cover_id=previous_land_cover_id
    )
    indicator["value"] = to_precision(number=value, digits=_OUTPUT_SIGNIFICANT_DIGITS) if value != 0 else 0
    return indicator


def _gap_filled_date_obj(date_str: str) -> datetime:
    return datetime.strptime(
        _gapfill_datestr(datestr=date_str, mode=DatestrGapfillMode.MIDDLE),
        DatestrFormat.YEAR_MONTH_DAY_HOUR_MINUTE_SECOND.value
    )


def _find_closest_node(
    ia_date_str: str,
    management_nodes: list,
    historic_date_offset: int,
    node_date_field: str
) -> str:
    historic_ia_date_obj = (
        _gap_filled_date_obj(ia_date_str) - relativedelta(years=historic_date_offset)
        if ia_date_str else None
    )
    # Calculate all distances in days which are less than MAXIMUM_OFFSET_DAYS from historic date
    # Assumption: if there are two dates are equidistant from the target, choose the second.
    filtered_dates = {
        abs((_gap_filled_date_obj(node.get(node_date_field)) - historic_ia_date_obj).days): node.get(node_date_field)
        for node in management_nodes
        if node.get("term", {}).get("termType", "") == TermTermType.LANDCOVER.value and
        abs((_gap_filled_date_obj(node.get(node_date_field)) - historic_ia_date_obj).days) <= _MAXIMUM_OFFSET_DAYS
    }
    return filtered_dates[min(filtered_dates.keys())] if filtered_dates else ""


def should_run(
    impact_assessment: dict,
    site: dict,
    term_id: str,
    historic_date_offset: int
) -> tuple[bool, dict, str, str]:
    relevant_emission_resource_use = [
        node for node in impact_assessment.get("emissionsResourceUse", [])
        if node.get("term", {}).get("@id", "") == _RESOURCE_USE_TERM_ID and node.get("value", -1) >= 0
    ]
    filtered_management_nodes = [
        node for node in site.get("management", [])
        if node.get("value", -1) >= 0 and node.get("term", {}).get("termType", "") == TermTermType.LANDCOVER.value
    ]
    land_occupation_during_cycle_found = any(
        node.get("term", {}).get("@id") in
        {node.get("landCover", {}).get("@id") for node in relevant_emission_resource_use}
        for node in filtered_management_nodes
    )
    match_mode = (
        DatestrGapfillMode.START if impact_assessment.get("cycle", {}).get("aggregated") is True
        else DatestrGapfillMode.END
    )
    match_date = "startDate" if match_mode == DatestrGapfillMode.START else "endDate"

    closest_date = _find_closest_node(
        ia_date_str=impact_assessment.get(match_date, ""),
        management_nodes=filtered_management_nodes,
        historic_date_offset=historic_date_offset,
        node_date_field=match_date
    )
    closest_start_date, closest_end_date = (closest_date, None) if match_date == "startDate" else (None, closest_date)
    current_node_index = next(
        (i for i, node in enumerate(filtered_management_nodes)
         if _str_dates_match(
            date_str_one=node.get(match_date, ""),
            date_str_two=impact_assessment.get(match_date, ""),
            mode=match_mode
        )),
        None
    )
    current_node = filtered_management_nodes.pop(current_node_index) if current_node_index is not None else None

    logRequirements(impact_assessment, model=MODEL, term=term_id,
                    closest_end_date=closest_end_date,
                    closest_start_date=closest_start_date,
                    has_landOccupationDuringCycle=land_occupation_during_cycle_found,
                    landCover_term_id=(current_node or {}).get('term', {}).get('@id'))

    should_run_result = all([
        relevant_emission_resource_use,
        land_occupation_during_cycle_found,
        current_node,
        closest_end_date or closest_start_date
    ])
    logShouldRun(impact_assessment, MODEL, term=term_id, should_run=should_run_result)

    return should_run_result, current_node, closest_end_date, closest_start_date


def _get_land_occupation_for_land_use_type(impact_assessment: dict, ipcc_land_use_category: str) -> float:
    """
    Returns the sum of all land occupation for the specified land_use_category.
    """
    return sum(
        node.get("value", 0) for node in impact_assessment.get("emissionsResourceUse", [])
        if node.get("term", {}).get("@id", "") == _RESOURCE_USE_TERM_ID
        and crop_ipcc_land_use_category(node.get("landCover", {}).get("@id", "")) == ipcc_land_use_category
    )


def _calculate_indicator_value(
    impact_assessment: dict,
    term_id: str,
    management_nodes: list,
    ipcc_land_use_category: str,
    previous_land_cover_id: str,
    historic_date_offset: int
) -> float:
    """
    Land transformation from [land type] previous management nodes
     = (Land occupation, during Cycle * Historic Site Percentage Area [land type] / 100) / HISTORIC_DATE_OFFSET
    """
    land_occupation_for_cycle = _get_land_occupation_for_land_use_type(
        impact_assessment=impact_assessment,
        ipcc_land_use_category=ipcc_land_use_category
    )
    historical_land_use = sum(
        node.get("value", 0) for node in management_nodes
        if node.get("term", {}).get("@id", "") == previous_land_cover_id
    )

    debugValues(impact_assessment, model=MODEL, term=term_id,
                ipcc_land_use_category=ipcc_land_use_category,
                land_occupation_for_cycle=land_occupation_for_cycle,
                historical_land_use=historical_land_use,
                historic_date_offset=historic_date_offset)

    return ((land_occupation_for_cycle * historical_land_use) / 100) / historic_date_offset


def _run_calculate_transformation(
    term_id: str,
    current_node: dict,
    closest_end_date: str,
    closest_start_date: str,
    impact_assessment: dict,
    site: dict,
    historic_date_offset: int
) -> list:
    """
    Calculate land transformation for all land use categories.
    """
    indicators = [
        _new_indicator_with_value(
            term_id=term_id,
            land_cover_id=current_node.get("term", {}).get("@id"),
            previous_land_cover_id=previous_land_cover_id,
            value=_calculate_indicator_value(
                impact_assessment=impact_assessment,
                term_id=term_id,
                management_nodes=[
                    node for node in site.get("management", [])
                    if _str_dates_match(node.get("endDate", ""), closest_end_date) or
                    _str_dates_match(node.get("startDate", ""), closest_start_date)
                ],
                ipcc_land_use_category=crop_ipcc_land_use_category(current_node.get("term", {}).get("@id", "")),
                previous_land_cover_id=previous_land_cover_id,
                historic_date_offset=historic_date_offset
            )
        ) for previous_land_cover_id in [t[0] for t in LAND_USE_TERMS_FOR_TRANSFORMATION.values()]
    ]

    return indicators


def run_resource_use(
    impact_assessment: dict,
    historic_date_offset: int,
    term_id: str
) -> list:
    site = get_site(impact_assessment)
    _should_run, current_node, closest_end_date, closest_start_date = should_run(
        impact_assessment=impact_assessment,
        site=site,
        term_id=term_id,
        historic_date_offset=historic_date_offset
    )
    return _run_calculate_transformation(
        impact_assessment=impact_assessment,
        site=site,
        term_id=term_id,
        current_node=current_node,
        closest_end_date=closest_end_date,
        closest_start_date=closest_start_date,
        historic_date_offset=historic_date_offset
    ) if _should_run else []
