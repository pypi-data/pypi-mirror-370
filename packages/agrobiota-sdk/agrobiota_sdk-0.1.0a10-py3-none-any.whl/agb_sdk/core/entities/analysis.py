from abc import ABC, abstractmethod
from typing import Any
from uuid import UUID

from agb_sdk.core.dtos import AnalysisList, BiotropBioindex


class AnalysisEntity(ABC):
    @abstractmethod
    async def list_analysis(
        self,
        term: str | None = None,
        skip: int | None = None,
        size: int | None = None,
        **_: Any,
    ) -> tuple[AnalysisList | None, int | None]: ...

    @abstractmethod
    async def get_bioindex_by_id(
        self,
        bioindex_id: UUID,
        **_: Any,
    ) -> tuple[BiotropBioindex | None, int | None]: ...
