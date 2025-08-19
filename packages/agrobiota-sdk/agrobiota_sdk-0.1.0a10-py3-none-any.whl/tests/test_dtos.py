import logging

import pytest

from agb_sdk.core.dtos import BiotropBioindex, CustomerRecord, Locale

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


@pytest.fixture
def sample_bioindex_data():
    raw_data = None

    with open("src/tests/mock/expected-bioidnex-data.jsonc", "r") as file:
        raw_data = file.read()

    assert raw_data is not None
    assert isinstance(raw_data, str)

    bioindex = BiotropBioindex.model_validate_json(raw_data)

    assert bioindex is not None
    assert isinstance(bioindex, BiotropBioindex)

    bioindex.set_locale(locale=Locale.PT_BR)

    return bioindex


@pytest.fixture
def sample_customer_record_data():
    raw_data = None

    with open("src/tests/mock/customer-record.jsonc", "r") as file:
        raw_data = file.read()

    assert raw_data is not None
    assert isinstance(raw_data, str)

    customer_record = CustomerRecord.model_validate_json(raw_data)

    assert customer_record is not None
    assert isinstance(customer_record, CustomerRecord)

    return customer_record


def test_stability_on_deserialization_of_biotrop_bioindex(
    sample_bioindex_data: BiotropBioindex,
) -> None:
    logger.info("Testing BiotropBioindex")

    assert sample_bioindex_data.id == "4c3ed2bf-8cda-41c8-b168-2a4cfecga74c"
    assert sample_bioindex_data.hash == "00000000000000000000000000000000"
    assert sample_bioindex_data.version == 1
    assert sample_bioindex_data.updated_at == "2021-05-27 00:01:48.651 +00:00"
    assert len(sample_bioindex_data.results) == 2
    assert len(sample_bioindex_data.results[0].diversity.community_composition) == 34
    assert len(sample_bioindex_data.results[1].diversity.community_composition) == 24

    print(sample_bioindex_data.model_dump())


async def test_resolve_taxonomy_of_biotrop_bioindex(
    sample_bioindex_data: BiotropBioindex,
) -> None:
    result = await sample_bioindex_data.resolve_taxonomies()

    assert result is not None
    assert isinstance(result, BiotropBioindex)

    assert len(result.results[0].diversity.community_composition) == 34
    assert len(result.results[1].diversity.community_composition) == 24

    expected_taxons = [
        record.taxon for record in result.results[0].diversity.community_composition
    ]

    for taxon in ["Burkholderia", "Kocuria"]:
        assert taxon in expected_taxons


async def test_customer_record_deserialization(
    sample_customer_record_data: CustomerRecord,
) -> None:
    logger.info("Testing CustomerRecord")

    sample_customer_record_data._set_locale(locale=Locale.PT_BR)
