import logging
from pathlib import Path

import pytest

from agb_sdk.core.dtos import BiotropBioindex
from agb_sdk.core.use_cases import convert_bioindex_to_tabular

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


@pytest.fixture
def sample_data():
    raw_data = None

    with open("src/tests/mock/expected-bioidnex-data.jsonc", "r") as file:
        raw_data = file.read()

    assert raw_data is not None
    assert isinstance(raw_data, str)

    bioindex = BiotropBioindex.model_validate_json(raw_data)

    assert bioindex is not None
    assert isinstance(bioindex, BiotropBioindex)

    return bioindex


async def test_convert_bioindex_to_tabular(sample_data: BiotropBioindex):
    output_path = "/tmp/expected-bioindex-data.xlsx"

    await convert_bioindex_to_tabular(
        bioindex=sample_data,
        output_path=output_path,
        resolve_taxonomies=True,
    )

    assert Path(output_path).exists()
    assert Path(output_path).is_file()

    # TODO: Add more assertions
