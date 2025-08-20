from unittest.mock import Mock, patch
import json
from tests.utils import fixtures_path, fake_new_measurement

from hestia_earth.models.hestia.waterSalinity import MODEL, TERM_ID, run

class_path = f"hestia_earth.models.{MODEL}.{TERM_ID}"
fixtures_folder = f"{fixtures_path}/{MODEL}/{TERM_ID}"


@patch(f"{class_path}._new_measurement", side_effect=fake_new_measurement)
@patch(f"{class_path}.related_cycles")
def test_run(mock_related_cycles: Mock, *args):
    with open(f"{fixtures_folder}/site.jsonld", encoding='utf-8') as f:
        site = json.load(f)

    with open(f"{fixtures_folder}/cycles.jsonld", encoding='utf-8') as f:
        cycles = json.load(f)

    mock_related_cycles.return_value = cycles

    with open(f"{fixtures_folder}/result.jsonld", encoding='utf-8') as f:
        expected = json.load(f)

    value = run(site)
    assert value == expected
