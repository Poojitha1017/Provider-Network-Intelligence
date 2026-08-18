from typing import Optional
from fastapi import APIRouter, Query
from app.schemas.provider import PaginatedProviderResponse
from app.services.provider_service import provider_service

router = APIRouter(prefix="/providers", tags=["Providers"])


@router.get("", response_model=PaginatedProviderResponse)
async def get_providers(
    county_fips: Optional[str] = Query(None, description="County FIPS code (e.g. '48183')"),
    state: Optional[str] = Query(None, description="State name"),
    city: Optional[str] = Query(None, description="City name"),
    specialty: Optional[str] = Query(None, description="Provider specialty (e.g. 'Cardiology')"),
    disease: Optional[str] = Query(None, description="Disease focus"),
    telehealth: Optional[bool] = Query(None, description="Filter for telehealth availability"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Page size"),
):
    """
    Retrieves in-network provider records matching filter criteria.
    """
    return provider_service.get_providers(
        county_fips=county_fips,
        state=state,
        city=city,
        specialty=specialty,
        disease=disease,
        telehealth=telehealth,
        page=page,
        page_size=page_size,
    )
