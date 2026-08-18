from typing import Optional
from fastapi import APIRouter, Query
from app.schemas.decision import PaginatedAccessGapResponse
from app.services.decision_service import decision_service

router = APIRouter(prefix="/access-gaps", tags=["Access Gaps"])


@router.get("", response_model=PaginatedAccessGapResponse)
async def get_access_gaps(
    county_fips: Optional[str] = Query(None, description="County FIPS code"),
    specialty: Optional[str] = Query(None, description="Required specialty"),
    disease: Optional[str] = Query(None, description="Disease name"),
    risk_level: Optional[str] = Query(None, description="Access gap risk level"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
):
    """
    Retrieves calculated access gap intelligence metrics from the `decision` table.
    """
    return decision_service.get_access_gaps(
        county_fips=county_fips,
        specialty=specialty,
        disease=disease,
        risk_level=risk_level,
        page=page,
        page_size=page_size,
    )
