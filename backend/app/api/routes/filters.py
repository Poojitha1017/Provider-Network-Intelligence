from typing import Optional, List
from fastapi import APIRouter, Query
from app.schemas.filters import FilterOptionsResponse
from app.services.filter_service import filter_service

router = APIRouter(prefix="/filters", tags=["Filters"])


@router.get("/options", response_model=FilterOptionsResponse)
async def get_filter_options(
    county_fips: Optional[str] = Query(None, description="Filter by County FIPS code (e.g. '48183')"),
    city: Optional[str] = Query(None, description="Filter by City name"),
    disease: Optional[str] = Query(None, description="Filter by Disease name"),
    specialty: Optional[str] = Query(None, description="Filter by Specialty name"),
    risk_level: Optional[str] = Query(None, description="Filter by Risk level"),
    state: Optional[str] = Query(None, description="Filter by State name"),
):
    """
    Dynamically returns valid filter options based on currently selected filters
    by querying the `uc05_filter_options` table.
    """
    return filter_service.get_options(
        county_fips=county_fips,
        city=city,
        disease=disease,
        specialty=specialty,
        risk_level=risk_level,
        state=state,
    )


@router.get("/states", response_model=List[str])
async def get_states():
    """
    Returns unique list of monitored states.
    """
    options = filter_service.get_options()
    return options.states


@router.get("/cities", response_model=List[str])
async def get_cities(state: Optional[str] = None):
    """
    Returns unique list of monitored cities (optionally scoped by state).
    """
    options = filter_service.get_options(state=state)
    return options.cities


@router.get("/diseases", response_model=List[str])
async def get_diseases(specialty: Optional[str] = None):
    """
    Returns unique list of monitored diseases.
    """
    options = filter_service.get_options(specialty=specialty)
    return options.diseases


@router.get("/specialties", response_model=List[str])
async def get_specialties(disease: Optional[str] = None):
    """
    Returns unique list of monitored specialties.
    """
    options = filter_service.get_options(disease=disease)
    return options.specialties


@router.get("/risk-levels", response_model=List[str])
async def get_risk_levels(county_fips: Optional[str] = None, specialty: Optional[str] = None):
    """
    Returns unique list of risk levels.
    """
    options = filter_service.get_options(county_fips=county_fips, specialty=specialty)
    return options.risk_levels
