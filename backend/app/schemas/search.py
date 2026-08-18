from typing import List, Optional, Any, Dict
from pydantic import BaseModel, Field


class SearchResultItem(BaseModel):
    county_fips: Optional[str] = None
    state: Optional[str] = None
    city: Optional[str] = None
    disease: Optional[str] = None
    specialty: Optional[str] = None
    risk_level: Optional[str] = None
    risk_score: Optional[float] = None
    provider_count: Optional[int] = None
    estimated_patients: Optional[int] = None
    patients_per_provider: Optional[float] = None
    gap_ratio: Optional[float] = None
    access_gap_level: Optional[str] = None
    extra_metadata: Optional[Dict[str, Any]] = None


class PaginatedSearchResponse(BaseModel):
    total: int = Field(..., description="Total matching items count")
    page: int = Field(1, description="Current page number")
    page_size: int = Field(20, description="Items per page")
    total_pages: int = Field(1, description="Total number of pages")
    results: List[SearchResultItem] = Field(default_factory=list, description="Search results")
