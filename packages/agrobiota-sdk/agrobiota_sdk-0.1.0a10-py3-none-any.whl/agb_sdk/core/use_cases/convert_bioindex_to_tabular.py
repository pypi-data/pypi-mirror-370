from pathlib import Path
from typing import Any

from pandas import DataFrame, ExcelWriter

from agb_sdk.core.dtos import BiotropBioindex, Locale, GGHDimension


async def convert_bioindex_to_tabular(
    bioindex: BiotropBioindex,
    output_path: Path | None = None,
    resolve_taxonomies: bool = True,
    **kwargs,
) -> tuple[DataFrame, DataFrame, DataFrame, DataFrame, DataFrame, DataFrame] | None:
    """Convert a BiotropBioindex to a Pandas DataFrame"""

    by_sample_data: list[dict[str, Any]] = []
    by_dimension_data: list[dict[str, Any]] = []
    by_process_data: list[dict[str, Any]] = []
    diversity_data: list[dict[str, Any]] = []
    community_composition_data: list[dict[str, Any]] = []

    # --------------------------------------------------------------------------
    # 0. Resolve taxonomies
    # --------------------------------------------------------------------------

    if resolve_taxonomies:
        bioindex = await bioindex.resolve_taxonomies(**kwargs)

    # --------------------------------------------------------------------------
    # 1. Summary data
    # --------------------------------------------------------------------------

    info_dataframe = DataFrame.from_records(
        [
            {
                "id": bioindex.id,
                "hash": bioindex.hash,
                "version": bioindex.version,
                "updated_at": bioindex.updated_at,
            }
        ],
    ).transpose()

    info_dataframe.columns = ["info"]

    # --------------------------------------------------------------------------
    # 2. By sample data
    # --------------------------------------------------------------------------

    for result in bioindex.results:
        by_sample_data.append(
            {
                "sample": result.sample,
                "ggh": result.ggh,
            }
        )

    by_sample_dataframe = DataFrame.from_records(by_sample_data)

    # --------------------------------------------------------------------------
    # 3. By dimension data
    # --------------------------------------------------------------------------

    for result in bioindex.results:
        by_dimension_data.extend(
            [
                {
                    "sample": result.sample,
                    "dimension": "biodiversity",
                    "ggh": result.by_dimension.biodiversity.ggh,
                },
                {
                    "sample": result.sample,
                    "dimension": "biological_agents",
                    "ggh": result.by_dimension.biological_agents.ggh,
                },
                {
                    "sample": result.sample,
                    "dimension": "biological_fertility",
                    "ggh": result.by_dimension.biological_fertility.ggh,
                },
                {
                    "sample": result.sample,
                    "dimension": "phytosanitary_risk",
                    "ggh": result.by_dimension.phytosanitary_risk.ggh,
                },
            ]
        )

    by_dimension_dataframe = DataFrame.from_records(by_dimension_data)

    # --------------------------------------------------------------------------
    # 4. By process data
    # --------------------------------------------------------------------------

    for result in bioindex.results:
        for group, data in [
            (
                GGHDimension.Biodiversity,
                result.by_dimension.biodiversity.by_process,
            ),
            (
                GGHDimension.BiologicalAgents,
                result.by_dimension.biological_agents.by_process,
            ),
            (
                GGHDimension.BiologicalFertility,
                result.by_dimension.biological_fertility.by_process,
            ),
            (
                GGHDimension.PhytosanitaryRisk,
                result.by_dimension.phytosanitary_risk.by_process,
            ),
        ]:
            for process in data:
                process_data = {
                    "sample": result.sample,
                    "dimension": group.value,
                    "process": process.process,
                    "ggh": process.ggh,
                }

                if hasattr(process, "group"):
                    process_data.update({"group": process.group})

                by_process_data.append(process_data)

    by_process_dataframe = DataFrame.from_records(by_process_data)

    # --------------------------------------------------------------------------
    # 5. Diversity data
    # --------------------------------------------------------------------------

    for result in bioindex.results:
        diversity_data.extend(
            [
                {
                    "sample": result.sample,
                    "taxon": "bacteria",
                    "faith_pd": result.diversity.statistics.faith_pd.bacteria.value,
                    "shannon": result.diversity.statistics.shannon.bacteria.value,
                    "richness": result.diversity.statistics.richness.bacteria.value,
                    "faith_pd_inverse_confidence": result.diversity.statistics.faith_pd.bacteria.inverse_confidence,
                    "shannon_inverse_confidence": result.diversity.statistics.shannon.bacteria.inverse_confidence,
                    "richness_inverse_confidence": result.diversity.statistics.richness.bacteria.inverse_confidence,
                },
                {
                    "sample": result.sample,
                    "taxon": "fungi",
                    "faith_pd": result.diversity.statistics.faith_pd.fungi.value,
                    "shannon": result.diversity.statistics.shannon.fungi.value,
                    "richness": result.diversity.statistics.richness.fungi.value,
                    "faith_pd_inverse_confidence": result.diversity.statistics.faith_pd.fungi.inverse_confidence,
                    "shannon_inverse_confidence": result.diversity.statistics.shannon.fungi.inverse_confidence,
                    "richness_inverse_confidence": result.diversity.statistics.richness.fungi.inverse_confidence,
                },
            ]
        )

    diversity_dataframe = DataFrame.from_records(diversity_data)

    # --------------------------------------------------------------------------
    # 6. Community composition data
    # --------------------------------------------------------------------------

    for result in bioindex.results:
        for taxon in result.diversity.community_composition:
            community_composition_data.extend(
                [
                    {
                        "sample": result.sample,
                        "taxon": taxon.taxon,
                        "taxon_id": taxon.key,
                        "count": taxon.count,
                        "is_pathogenic": taxon.is_pathogenic,
                    }
                ]
            )

    community_composition_dataframe = DataFrame.from_records(
        community_composition_data,
    )

    # --------------------------------------------------------------------------
    # 7. Persist as XLSX separated by tabs
    # --------------------------------------------------------------------------

    if output_path is not None and isinstance(output_path, Path):
        if not output_path.parent.exists():
            output_path.parent.mkdir(parents=True)

        output_path = output_path.with_suffix(".xlsx")

        with ExcelWriter(output_path, mode="w") as writer:
            info_dataframe.to_excel(writer, sheet_name="summary")
            by_sample_dataframe.to_excel(writer, sheet_name="by_sample")
            by_dimension_dataframe.to_excel(writer, sheet_name="by_dimension")
            by_process_dataframe.to_excel(writer, sheet_name="by_process")
            diversity_dataframe.to_excel(writer, sheet_name="diversity")
            community_composition_dataframe.to_excel(
                writer, sheet_name="community_composition"
            )

        return None

    # --------------------------------------------------------------------------
    # 8. Return the dataframes
    # --------------------------------------------------------------------------

    return (
        info_dataframe,
        by_sample_dataframe,
        by_dimension_dataframe,
        by_process_dataframe,
        diversity_dataframe,
        community_composition_dataframe,
    )


def __translate_key(
    model_config: dict[str, Any],
    key: str,
    locale: Locale | None = None,
    default_key: str | None = None,
) -> str:
    """Translate a key using the provided translations dictionary."""

    if locale is None:
        return default_key or key

    if (translations := model_config.get("_translations")) is None:
        return default_key or key

    if not isinstance(translations, dict):
        return default_key or key

    if (locale_translations := translations.get(locale.value)) is None:
        return default_key or key

    if isinstance(locale_translations, dict):
        return locale_translations.get(key, default_key or key)

    return default_key or key
