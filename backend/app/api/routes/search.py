from typing import Optional
from fastapi import APIRouter, Query
from app.schemas.search import PaginatedSearchResponse
from app.services.search_service import search_service

router = APIRouter(prefix="/search", tags=["Search"])


@router.get("", response_model=PaginatedSearchResponse)
async def search(
    county_fips: Optional[str] = Query(None, description="County FIPS code"),
    state: Optional[str] = Query(None, description="State name"),
    city: Optional[str] = Query(None, description="City name"),
    disease: Optional[str] = Query(None, description="Disease name"),
    specialty: Optional[str] = Query(None, description="Specialty name"),
    risk_level: Optional[str] = Query(None, description="Risk level (e.g. 'CRITICAL GAP', 'HIGH GAP')"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
):
    """
    Main search API querying access gap records, provider supply, and intelligence metrics.
    """
    return search_service.search(
        county_fips=county_fips,
        state=state,
        city=city,
        disease=disease,
        specialty=specialty,
        risk_level=risk_level,
        page=page,
        page_size=page_size,
    )
