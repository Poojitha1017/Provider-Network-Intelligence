from typing import List, Optional
from pydantic import BaseModel, Field


class Provider(BaseModel):
    id: Optional[int] = None
    npi: Optional[str] = None
    provider_name: Optional[str] = None
    primary_specialty: Optional[str] = None
    secondary_specialty: Optional[str] = None
    state: Optional[str] = None
    city: Optional[str] = None
    zip: Optional[str] = None
    county: Optional[str] = None
    county_fips: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    telehealth: Optional[bool] = None
    facility_name: Optional[str] = None
    tot_benes: Optional[int] = None
    tot_srvcs: Optional[int] = None
    bene_avg_risk_scre: Optional[float] = None
    total_utilization_exact: Optional[float] = None
    avg_utilization_percentile: Optional[float] = None
    disease: Optional[str] = None


class PaginatedProviderResponse(BaseModel):
    total: int = Field(..., description="Total count of matching records")
    page: int = Field(1, description="Current page number")
    page_size: int = Field(20, description="Number of items per page")
    total_pages: int = Field(1, description="Total number of pages")
    providers: List[Provider] = Field(default_factory=list, description="List of providers")
