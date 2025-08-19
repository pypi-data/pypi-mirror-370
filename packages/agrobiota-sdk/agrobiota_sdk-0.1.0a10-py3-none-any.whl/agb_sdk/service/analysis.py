import logging
from typing import Any
from uuid import UUID

from aiohttp import ClientSession
from termcolor import colored

from agb_sdk.core.dtos import AnalysisList, BiotropBioindex
from agb_sdk.core.entities.analysis import AnalysisEntity
from agb_sdk.core.exceptions import GetBioindexByIdException, ListAnalysisException
from agb_sdk.settings import DEFAULT_CONNECTION_STRING_HEADER, DEFAULT_CUSTOMERS_API_URL

logger = logging.getLogger(__name__)


class AnalysisService(AnalysisEntity):
    __connection_string: str
    __custom_api_url: str | None = DEFAULT_CUSTOMERS_API_URL

    def __init__(
        self,
        connection_string: str,
        custom_api_url: str | None = None,
    ) -> None:
        self.__connection_string = connection_string

        if custom_api_url:
            self.__custom_api_url = custom_api_url

    async def list_analysis(
        self,
        term: str | None = None,
        skip: int | None = None,
        size: int | None = None,
        **_: Any,
    ) -> tuple[AnalysisList | None, int | None]:
        params: dict[str, Any] = {}

        if term:
            params.update({"term": term})

        if skip:
            params.update({"skip": skip})

        if size:
            params.update({"size": size})

        try:
            analysis_list: AnalysisList | None = None
            response_status: int | None = None

            async with ClientSession() as session:
                async with session.get(
                    f"{self.__custom_api_url}/analysis",
                    timeout=120,
                    headers={
                        DEFAULT_CONNECTION_STRING_HEADER: self.__connection_string,
                    },
                    params=params,
                ) as response:
                    if response.status not in [200, 204]:
                        return self.__handle_error_response(
                            status=response.status,
                            exc=ListAnalysisException,
                        )

                    content_type = response.headers.get("Content-Type")
                    raw_records = await response.json(content_type=content_type)

                    analysis_list = AnalysisList.model_validate(raw_records)
                    response_status = response.status

            return analysis_list, response_status

        except ListAnalysisException as e:
            raise e

        except Exception as e:
            raise e

    async def get_bioindex_by_id(
        self,
        bioindex_id: UUID,
        **_: Any,
    ) -> tuple[BiotropBioindex | None, int | None]:
        try:
            biotrop_bioindex: BiotropBioindex | None = None
            response_status: int | None = None

            async with ClientSession() as session:
                async with session.get(
                    f"{self.__custom_api_url}/analysis/bioindex/{bioindex_id}",
                    timeout=120,
                    headers={
                        DEFAULT_CONNECTION_STRING_HEADER: self.__connection_string,
                    },
                ) as response:
                    if response.status not in [200, 204]:
                        return self.__handle_error_response(
                            status=response.status,
                            exc=GetBioindexByIdException,
                        )

                    content_type = response.headers.get("Content-Type")
                    raw_records = await response.json(content_type=content_type)

                    biotrop_bioindex = BiotropBioindex.model_validate(raw_records)
                    response_status = response.status

            return biotrop_bioindex, response_status

        except GetBioindexByIdException as e:
            raise e

        except Exception as e:
            raise e

    @staticmethod
    def __handle_error_response(status: int, exc: Exception) -> tuple[None, int]:
        """Handle error responses from the API."""
        default_return = (None, status)

        if status == 401:
            raise exc(
                colored(
                    f"\n[ UNAUTHENTICATED ACCESS | {status} ] Please check your connection string\n",
                    "yellow",
                )
            )

        if status == 403:
            raise exc(
                colored(
                    f"\n[ UNAUTHORIZED ACCESS | {status} ] You do not have permission to view this resource\n",
                    "yellow",
                )
            )

        raise f"Unexpected error on fetching data: {status}"
