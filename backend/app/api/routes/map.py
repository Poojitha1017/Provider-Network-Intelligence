from typing import Optional
from fastapi import APIRouter, Query
from app.schemas.map import MapAreasResponse
from app.services.decision_service import decision_service

router = APIRouter(prefix="/map", tags=["Map"])


@router.get("/areas", response_model=MapAreasResponse)
async def get_map_areas(
    county_fips: Optional[str] = Query(None, description="County FIPS code"),
    state: Optional[str] = Query(None, description="State name"),
    city: Optional[str] = Query(None, description="City name"),
    disease: Optional[str] = Query(None, description="Disease focus"),
    specialty: Optional[str] = Query(None, description="Specialty name"),
    risk_level: Optional[str] = Query(None, description="Risk level tier"),
):
    """
    Returns dynamic geographic and access gap records for map rendering,
    including area coordinates, risk scores, provider counts, and per-disease breakdowns.
    """
    return decision_service.get_map_areas(
        county_fips=county_fips,
        state=state,
        city=city,
        disease=disease,
        specialty=specialty,
        risk_level=risk_level,
    )
