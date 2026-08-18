from typing import Optional
from fastapi import APIRouter, Query
from app.schemas.decision import RecommendationsDataResponse
from app.services.recommendation_service import recommendation_service

router = APIRouter(prefix="/recommendations", tags=["Recommendations"])


@router.get("", response_model=RecommendationsDataResponse)
async def get_recommendations(
    state: Optional[str] = Query(None, description="State filter"),
    specialty: Optional[str] = Query(None, description="Specialty filter"),
    risk_level: Optional[str] = Query(None, description="Risk level filter"),
):
    """
    Returns prioritized recruitment recommendations ranked by expected impact score
    along with summary recruitment metrics.
    """
    return recommendation_service.get_recommendations(
        state=state,
        specialty=specialty,
        risk_level=risk_level,
    )
