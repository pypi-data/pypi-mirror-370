import logging
from typing import Any

from agb_sdk.core.dtos import AnalysisList, BiotropBioindex
from agb_sdk.core.entities.analysis import AnalysisEntity

logger = logging.getLogger(__name__)


async def list_analysis(
    analysis_service: AnalysisEntity,
    **kwargs: Any,
) -> tuple[AnalysisList | None, BiotropBioindex | None, int | None]:
    """List my analysis from AGROBIOTA Customers API"""

    if not isinstance(analysis_service, AnalysisEntity):
        logger.debug("Internal error: analysis_service is not an AnalysisEntity")
        logger.error("Internal error: please report this issue to the developers")
        return None, 500

    try:
        return await analysis_service.list_analysis(**kwargs)
    except Exception as e:
        logger.exception(e)
        return None, 500
