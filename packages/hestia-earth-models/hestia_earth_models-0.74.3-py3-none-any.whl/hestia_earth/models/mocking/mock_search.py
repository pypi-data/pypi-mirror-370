import json

from hestia_earth.models.utils import term

_original_search_func = term.search
_original_find_node_func = term.find_node


def _load_results(filepath: str):
    with open(filepath) as f:
        return json.load(f)


def _find_search_result(filepath: str, query: dict):
    search_results = _load_results(filepath)
    res = next((n for n in search_results if n['query'] == query), None)
    return None if res is None else res.get('results', [])


def _mocked_search(filepath: str):
    def mock(query: dict, **kwargs):
        result = _find_search_result(filepath, query)
        return _original_search_func(query, **kwargs) if result is None else result
    return mock


def _mocked_find_node(filepath: str):
    def mock(node_type: str, query: dict, **kwargs):
        result = _find_search_result(filepath, query)
        return _original_find_node_func(node_type, query, **kwargs) if result is None else result
    return mock


def mock(filepath: str):
    term.search = _mocked_search(filepath)
    term.find_node = _mocked_find_node(filepath)
