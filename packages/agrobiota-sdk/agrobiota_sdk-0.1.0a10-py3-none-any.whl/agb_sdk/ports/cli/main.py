import asyncio
import logging
from enum import Enum
from functools import wraps
from os import getenv
from pathlib import Path
from typing import Any
from uuid import UUID

import rich_click as click

from agb_sdk.__version__ import version
from agb_sdk.core.dtos import AnalysisList, BiotropBioindex, Locale
from agb_sdk.core.use_cases import (
    get_bioindex_by_id,
    list_analysis,
)
from agb_sdk.settings import DEFAULT_TAXONOMY_URL

logger = logging.getLogger(__name__)

ENV_LOG_LEVEL = getenv("LOG_LEVEL", "INFO").upper()
if ENV_LOG_LEVEL not in logging._nameToLevel:
    logger.warning(f"Invalid LOG_LEVEL: {ENV_LOG_LEVEL}. Defaulting to INFO level.")
    ENV_LOG_LEVEL = "INFO"

logger.setLevel(ENV_LOG_LEVEL)


# ------------------------------------------------------------------------------
# AUXILIARY ELEMENTS
# ------------------------------------------------------------------------------


def __extend_options(options: list[Any]) -> Any:
    def _extend_options(func: Any) -> Any:
        for option in reversed(options):
            func = option(func)
        return func

    return _extend_options


def __async_cmd(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        return asyncio.run(func(*args, **kwargs))

    return wrapper


def __async_inject_dependencies(func):
    """Decorator to inject dependencies into async Click commands."""

    @wraps(func)
    def wrapper(*args, **kwargs):
        from agb_sdk.service.analysis import AnalysisService

        kwargs.update(
            {
                "analysis_service": AnalysisService(
                    connection_string=kwargs.get("connection_string"),
                    custom_api_url=kwargs.get("custom_api_url"),
                )
            }
        )

        return func(*args, **kwargs)

    return wrapper


class OutputFormat(Enum):
    TABULAR = "tabular"
    JSON_RECORDS = "json-records"
    JSON_RAW = "json-raw"


# ------------------------------------------------------------------------------
# GROUPS DEFINITIONS
# ------------------------------------------------------------------------------


@click.group(
    "agb-sdk",
    help="Agrobiota SDK CLI",
)
@click.version_option(version)
def main():
    pass


@main.group(
    "convert",
    help="Convert data between formats",
)
def convert_group():
    pass


@main.group(
    "analysis",
    help="Operations over analysis from Agroportal API",
)
def analysis_group():
    pass


# ------------------------------------------------------------------------------
# SHARED OPTIONS DEFINITIONS
# ------------------------------------------------------------------------------


__TAXONOMY_RELATED_OPTIONS = [
    click.option(
        "--not-resolve-taxonomies",
        is_flag=True,
        default=False,
        show_default=True,
        help=(
            "If true, the taxonomies will be resolved from the taxonomy "
            "service. Otherwise the TaxID values will be used as is. This "
            "command should be used when the `REPORT_ID` parameter is provided."
        ),
    ),
    click.option(
        "--taxonomy-url",
        type=str,
        default=DEFAULT_TAXONOMY_URL,
        show_default=True,
        envvar="TAXONOMY_URL",
        help=(
            "The URL to the taxonomy service. This command should be used when "
            "the `REPORT_ID` parameter is provided."
        ),
    ),
]


# ------------------------------------------------------------------------------
# SUPPORT FUNCTIONS
# ------------------------------------------------------------------------------


async def __print_biotrop_bioindex(
    biotrop_bioindex: BiotropBioindex,
    output_format: OutputFormat = OutputFormat.TABULAR,
    save_to_file: str | None = None,
    locale: Locale | None = None,
    **kwargs,
) -> None:
    try:
        output_format = OutputFormat(output_format)
    except ValueError:
        raise click.ClickException(
            f"Invalid output format: {output_format}. "
            f"Supported formats are: {[e.value for e in OutputFormat]}"
        )

    if locale is not None:
        try:
            locale = Locale(locale)
        except ValueError:
            logger.warning(f"Invalid locale ({locale}), default value used")

    # --------------------------------------------------------------------------
    # If the desired output format is JSON_RAW and no file is specified,
    # we print the raw JSON to stdout.
    # --------------------------------------------------------------------------
    if output_format == OutputFormat.JSON_RAW and save_to_file is None:
        from json import dumps
        from sys import stdout

        if locale is not None:
            biotrop_bioindex.set_locale(locale)

        stdout.write(dumps(biotrop_bioindex.model_dump(), indent=4))
        return

    # --------------------------------------------------------------------------
    # If the desired output format is JSON_RAW and a file is specified,
    # we save the raw JSON to the specified file.
    # --------------------------------------------------------------------------
    if output_format == OutputFormat.JSON_RAW and save_to_file is not None:
        with open(save_to_file, "w") as f:
            f.write(biotrop_bioindex.model_dump_json(indent=4))
        logger.info(f"Bioindex saved to {save_to_file}")
        return

    # --------------------------------------------------------------------------
    # Then, proceed to convert the Bioindex processing with taxonomy resolution
    # if needed.
    # --------------------------------------------------------------------------
    from agb_sdk.core.use_cases import convert_bioindex_to_tabular

    implicit_save_to_file = all(
        [save_to_file is not None, output_format == OutputFormat.TABULAR]
    )

    response = await convert_bioindex_to_tabular(
        biotrop_bioindex,
        output_path=(Path(save_to_file) if implicit_save_to_file else None),
        resolve_taxonomies=not kwargs.get("not_resolve_taxonomies"),
        taxonomy_url=kwargs.get("taxonomy_url"),
    )

    # --------------------------------------------------------------------------
    # If the save_to_file is specified, the convert_bioindex_to_tabular use case
    # already handles saving the output to the file. Them we just return
    # and do not print the DataFrames.
    # --------------------------------------------------------------------------
    if implicit_save_to_file:
        logger.info(f"Bioindex saved to {save_to_file}")
        return

    # --------------------------------------------------------------------------
    # Otherwise, the tabular output should be further processed
    # --------------------------------------------------------------------------
    if response is None:
        raise click.ClickException(
            "An unexpected error occurred while generate output artifacts"
        )

    (
        info_data_frame,
        by_sample_data_frame,
        by_dimension_data_frame,
        by_process_data_frame,
        diversity_data_frame,
        community_composition_data_frame,
    ) = response

    # --------------------------------------------------------------------------
    # If the output format is JSON_RECORDS we convert the DataFrames to JSON
    # records and save them to the specified file or print them to stdout.
    # --------------------------------------------------------------------------
    if output_format == OutputFormat.JSON_RECORDS:
        from json import dumps
        from sys import stdout

        json_data = {
            **info_data_frame.to_dict(),
            "by_sample": by_sample_data_frame.to_dict(),
            "by_dimension": by_dimension_data_frame.to_dict(orient="records"),
            "by_process": by_process_data_frame.to_dict(orient="records"),
            "diversity": diversity_data_frame.to_dict(orient="records"),
            "community_composition": community_composition_data_frame.to_dict(
                orient="records"
            ),
        }

        if save_to_file is not None:
            save_to_file = Path(save_to_file).with_suffix(".json")

            with open(save_to_file, "w") as f:
                f.write(dumps(json_data, indent=4))
            logger.info(f"Bioindex saved to {save_to_file}")
            return

        stdout.write(dumps(json_data, indent=4))
        return

    # --------------------------------------------------------------------------
    # Otherwise, print the DataFrames in a tabular format using Rich
    # --------------------------------------------------------------------------
    from rich.console import Console
    from rich.table import Table

    console = Console()

    for name, print_index, database in [
        ("Bioindex Information", True, info_data_frame),
        ("Bioindex by Sample", False, by_sample_data_frame),
        ("Bioindex by Dimension", False, by_dimension_data_frame),
        ("Bioindex by Process", False, by_process_data_frame),
        ("Diversity Descriptors", False, diversity_data_frame),
        ("Community Composition", False, community_composition_data_frame),
    ]:
        table = Table(name)
        table.add_row(
            database.to_string(
                float_format=lambda _: "{:.2f}".format(_),
                index=print_index,
            )
        )
        console.print(table)


def __print_analysis_list(analysis_list: AnalysisList, **kwargs) -> None:
    import datetime

    from rich.console import Console
    from rich.table import Table

    def format_datetime(value):
        if isinstance(value, str):
            try:
                normalized = value.replace(" ", "T", 1).replace(" +", "+")
                value = datetime.datetime.fromisoformat(normalized)
            except Exception as e:
                print(e)
                return value  # return raw string if parsing fails

        return value.strftime("%d/%m/%Y %H:%M")

    # Create a Console object
    console = Console()

    page_size = kwargs.get("size", 25)
    page = kwargs.get("skip", 0)
    total_pages = (len(analysis_list.records) + page_size - 1) // page_size

    # Create a Table object
    table = Table(title="Analysis List")

    table.add_column("Name", justify="left", style="bold cyan")
    table.add_column("Updated At")
    table.add_column("Report IDs")

    for analysis in analysis_list.records:
        bioindex_ids = analysis.list_bioindex_ids()

        table.add_row(
            analysis.name,
            format_datetime(analysis.updated_at),
            "\n".join([f"{index + 1} {id}" for index, id in enumerate(bioindex_ids)]),
        )

    table.caption = f"Page {page + 1}/{total_pages}. Use -t to filter by term, -sk to skip records and -s to set the page size."
    table.caption_justify = "left"
    console.print(table)


# ------------------------------------------------------------------------------
# COMMANDS DEFINITIONS
# ------------------------------------------------------------------------------


@convert_group.command("bioindex-to-tabular")
@click.argument(
    "input_path",
    required=1,
    type=click.Path(exists=True),
)
@click.argument(
    "output_path",
    required=1,
    type=click.Path(),
)
@__extend_options(__TAXONOMY_RELATED_OPTIONS)
@__async_cmd
async def convert_bioindex_to_tabular_cmd(
    input_path: str,
    output_path: str,
    resolve_taxonomies: bool = True,
    **kwargs,
) -> None:

    bioindex: BiotropBioindex | None = None

    try:
        with open(input_path, "r") as f:
            bioindex = BiotropBioindex.model_validate_json(f.read())
    except Exception as e:
        raise click.ClickException(f"Error parsing bioindex: {e}")

    if bioindex is None:
        raise click.ClickException("Failed to parse bioindex")

    from agb_sdk.core.use_cases import convert_bioindex_to_tabular

    await convert_bioindex_to_tabular(
        bioindex,
        Path(output_path),
        resolve_taxonomies,
        **kwargs,
    )


@analysis_group.command("list")
@click.argument(
    "report_id",
    required=False,
    type=click.UUID,
)
@click.option(
    "--connection-string",
    type=click.STRING,
    required=True,
    show_default=True,
    show_envvar=True,
    envvar="AGB_CONNECTION_STRING",
    help="The connection string to the Agroportal API.",
)
@click.option(
    "-t",
    "--term",
    type=click.STRING,
    help="The term to search for in the analysis.",
)
@click.option(
    "-sk",
    "--skip",
    type=click.INT,
    default=0,
    show_default=True,
    help="The number of records to skip.",
)
@click.option(
    "-s",
    "--size",
    type=click.INT,
    default=25,
    show_default=True,
    help="The number of records to return.",
)
@click.option(
    "--save-to-file",
    type=click.Path(),
    default=None,
    show_default=True,
    required=False,
    help=(
        "If provided, the analysis will be saved to a file. This option is only "
        "available when the Biotrop Bioindex is provided."
    ),
)
@click.option(
    "-l",
    "--locale",
    type=click.Choice(
        [Locale.PT_BR.value],
        case_sensitive=False,
    ),
    default=None,
    required=False,
    show_default=True,
    help="The locale to use for translations.",
)
@click.option(
    "-f",
    "--output-format",
    type=click.Choice(
        [
            OutputFormat.TABULAR.value,
            OutputFormat.JSON_RECORDS.value,
            OutputFormat.JSON_RAW.value,
        ],
        case_sensitive=False,
    ),
    default="tabular",
    show_default=True,
    help=(
        "The format to use for the output. If 'tabular', the output will be "
        "formatted as a table. If 'json', the output will be formatted as JSON."
        " This option is only available when the Biotrop Bioindex is provided."
    ),
)
@__extend_options(__TAXONOMY_RELATED_OPTIONS)
@__async_cmd
@__async_inject_dependencies
async def list_analysis_or_bioindex_cmd(
    report_id: UUID | None = None,
    **kwargs,
) -> None:
    if report_id is None:
        analysis_list, response_status = await list_analysis(
            report_id=report_id,
            **kwargs,
        )

        if response_status == 200:
            __print_analysis_list(
                analysis_list=analysis_list,
                **kwargs,
            )

            return

        if response_status == 204:
            raise click.ClickException("No analysis to show")

        return

    if report_id is not None:
        bioindex, response_status = await get_bioindex_by_id(
            bioindex_id=report_id,
            **kwargs,
        )

        if response_status == 200:
            await __print_biotrop_bioindex(
                biotrop_bioindex=bioindex,
                **kwargs,
            )

        if response_status == 204:
            raise click.ClickException("No analysis to show")

        return

    raise click.ClickException(f"Failed to execute command")


# ------------------------------------------------------------------------------
# FIRE UP THE CLI IF THIS IS THE MAIN MODULE
# ------------------------------------------------------------------------------


if __name__ == "__main__":
    main()
