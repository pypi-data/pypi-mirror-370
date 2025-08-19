import logging
from typing import Any
from uuid import UUID

from agb_sdk.core.dtos import AnalysisList, BiotropBioindex
from agb_sdk.core.entities.analysis import AnalysisEntity

logger = logging.getLogger(__name__)


async def get_bioindex_by_id(
    analysis_service: AnalysisEntity,
    bioindex_id: str,
    **kwargs: Any,
) -> tuple[AnalysisList | None, BiotropBioindex | None, int | None]:
    if not isinstance(analysis_service, AnalysisEntity):
        logger.debug("Internal error: analysis_service is not an AnalysisEntity")
        logger.error("Internal error: please report this issue to the developers")
        return None, None

    if bioindex_id is None:
        logger.error("Bioindex ID must be provided")
        return None, 400

    if not isinstance(bioindex_id, UUID):
        try:
            bioindex_id = UUID(bioindex_id)
        except ValueError:
            logger.error("Invalid Bioindex ID format")
            return None, 400

    try:
        return await analysis_service.get_bioindex_by_id(bioindex_id, **kwargs)
    except Exception as e:
        logger.exception(e)
        return None, 500
