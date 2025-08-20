from typing import Optional
from hestia_earth.schema import TermTermType
from hestia_earth.utils.model import filter_list_term_type
from hestia_earth.utils.tools import list_sum, safe_parse_date

from hestia_earth.models.log import debugValues
from .lookup import all_factor_value, region_factor_value, aware_factor_value, fallback_country
from .product import find_by_product
from .site import region_level_1_id


def impact_end_year(impact_assessment: dict) -> int:
    """
    End year of the `ImpactAssessment`.

    Parameters
    ----------
    impact_assessment : dict
        The `ImpactAssessment`.

    Returns
    -------
    number
        The year in which the `ImpactAssessment` ends.
    """
    date = safe_parse_date(impact_assessment.get('endDate'))
    return date.year if date else None


def get_product(impact_assessment: dict) -> dict:
    """
    Get the full `Product` from the `ImpactAssessment`.
    Note: this is compatible with schema before version `21.0.0`.

    Parameters
    ----------
    impact_assessment : dict
        The `ImpactAssessment`.

    Returns
    -------
    dict
        The `Product` of the `ImpactAssessment`.
    """
    product = impact_assessment.get('product', {})
    return (product if 'term' in product else find_by_product(impact_assessment.get('cycle', {}), product)) or product


def get_site(impact_assessment: dict) -> dict:
    return impact_assessment.get('site') or impact_assessment.get('cycle', {}).get('site') or {}


def get_region_id(impact_assessment: dict, blank_node: dict = None) -> str:
    """
    Get the country or region @id of the ImpactAssessment.
    Note: level 1 GADM region will be returned only, even if the region is of level > 1.

    Parameters
    ----------
    impact_assessment : dict
        The `ImpactAssessment`.
    blank_node : dict
        If getting a value for a specific `emissionsResourceUse`, will try to get country from it.

    Returns
    -------
    str
        The `@id` of the `region`.
    """
    term_id: str = (
        (blank_node or {}).get('region') or
        (blank_node or {}).get('country') or
        impact_assessment.get('country') or
        get_site(impact_assessment).get('region') or
        get_site(impact_assessment).get('country') or
        {}
    ).get('@id')
    return (
        term_id if not term_id.startswith('GADM-') else
        region_level_1_id(term_id)
    ) if term_id else None


def get_country_id(impact_assessment: dict, blank_node: dict = None) -> str:
    """
    Get the country or @id of the ImpactAssessment.

    Parameters
    ----------
    impact_assessment : dict
        The `ImpactAssessment`.
    blank_node : dict
        If getting a value for a specific `emissionsResourceUse`, will try to get country from it.

    Returns
    -------
    str
        The `@id` of the `country`.
    """
    term_id = (
        (blank_node or {}).get('country') or
        impact_assessment.get('country') or
        get_site(impact_assessment).get('country') or
        {}
    ).get('@id')
    return term_id if term_id else None


def impact_emission_lookup_value(
    model: str, term_id: str, impact: dict, lookup_col: str, grouped_key: Optional[str] = None
) -> float:
    """
    Calculate the value of the impact based on lookup factors and emissions value.

    Parameters
    ----------
    model : str
        The model to display in the logs only.
    term_id : str
        The term to display in the logs only.
    impact : dict
        The `ImpactAssessment`.
    lookup_col : str
        The lookup column to fetch the factors from.
    grouped_key : str
        key of grouped data to extract in a lookup table

    Returns
    -------
    int
        The impact total value.
    """
    return all_factor_value(
        logs_model=model,
        logs_term_id=term_id,
        node=impact,
        lookup_name='emission.csv',
        lookup_col=lookup_col,
        blank_nodes=filter_list_term_type(impact.get('emissionsResourceUse', []), TermTermType.EMISSION),
        grouped_key=grouped_key,
        default_no_values=None
    )


def impact_country_value(
    logs_model: str,
    logs_term_id: str,
    impact: dict,
    lookup: str,
    group_key: str = None,
    country_fallback: bool = False,
    default_no_values=None
) -> float:
    """
    Calculate the value of the impact based on lookup factors and `site.country.@id`.

    Parameters
    ----------
    logs_model : str
        The model to display in the logs only.
    logs_term_id : str
        The term to display in the logs only.
    impact : dict
        The `ImpactAssessment`.
    lookup : str
        The name of the lookup to fetch the factors from.
    group_key : str
        Optional: key to use if the data is a group of values.
    country_fallback : bool
        Optional: if True fallback to default `region-world` country_id if country_id in `ImpactAssessment` not found in
        lookup file containing factors.

    Returns
    -------
    int
        The impact total value.
    """
    term_type = TermTermType.RESOURCEUSE.value if 'resourceUse' in lookup else TermTermType.EMISSION.value
    blank_nodes = filter_list_term_type(impact.get('emissionsResourceUse', []), term_type)

    country_id = get_country_id(impact)
    country_id = fallback_country(country_id, [lookup]) if country_fallback else country_id

    return all_factor_value(
        logs_model=logs_model,
        logs_term_id=logs_term_id,
        node=impact,
        lookup_name=lookup,
        lookup_col=country_id,
        blank_nodes=blank_nodes,
        grouped_key=group_key,
        default_no_values=default_no_values,
        factor_value_func=region_factor_value
    )


def impact_aware_value(model: str, term_id: str, impact: dict, lookup: str, group_key: str = None) -> float:
    """
    Calculate the value of the impact based on lookup factors and `site.awareWaterBasinId`.

    Parameters
    ----------
    model : str
        The model to display in the logs only.
    term_id : str
        The term to display in the logs only.
    impact_assessment : dict
        The `ImpactAssessment`.
    lookup : str
        The name of the lookup to fetch the factors from.
    group_key : str
        Optional: key to use if the data is a group of values.

    Returns
    -------
    int
        The impact total value.
    """
    blank_nodes = impact.get('emissionsResourceUse', [])
    site = get_site(impact)
    aware_id = site.get('awareWaterBasinId')

    return None if aware_id is None else all_factor_value(
        logs_model=model,
        logs_term_id=term_id,
        node=impact,
        lookup_name=lookup,
        lookup_col=aware_id,
        blank_nodes=blank_nodes,
        grouped_key=group_key,
        default_no_values=None,
        factor_value_func=aware_factor_value
    )


def impact_endpoint_value(model: str, term_id: str, impact: dict, lookup_col: str) -> float:
    """
    Calculate the value of the impact based on lookup factors and impacts value.

    Parameters
    ----------
    model : str
        Restrict the impacts by this model.
    term_id : str
        The term to display in the logs only.
    impact_assessment : dict
        The `ImpactAssessment`.
    lookup_col : str
        The lookup column to fetch the factors from.

    Returns
    -------
    int
        The impact total value.
    """
    nodes = [i for i in impact.get('impacts', []) if (
        i.get('methodModel').get('@id') == model or
        not i.get('methodModel').get('@id').startswith(model[0:6])  # allow other non-related models to be accounted for
    )]
    return all_factor_value(
        logs_model=model,
        logs_term_id=term_id,
        node=impact,
        lookup_name='characterisedIndicator.csv',
        lookup_col=lookup_col,
        blank_nodes=nodes,
        default_no_values=None
    )


def convert_value_from_cycle(
    log_node: dict, product: dict, value: float, default=None, model: str = None, term_id: str = None
):
    pyield = list_sum(product.get('value', [])) if product else 0
    economic_value = product.get('economicValueShare') if product else 0

    debugValues(log_node, model=model, term=term_id,
                product_yield=pyield,
                economicValueShare=economic_value)

    return (value / pyield) * economic_value / 100 if all([
        value is not None, pyield > 0, economic_value
    ]) else default
