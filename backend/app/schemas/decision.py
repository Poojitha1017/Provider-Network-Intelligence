from typing import List, Optional, Literal
from pydantic import BaseModel, Field


class AccessGapItem(BaseModel):
    id: Optional[int] = None
    county_fips: Optional[str] = None
    state: Optional[str] = None
    required_specialty: Optional[str] = None
    estimated_patients: Optional[int] = None
    provider_count: Optional[int] = None
    total_beneficiaries: Optional[int] = None
    total_services: Optional[int] = None
    patients_per_provider: Optional[float] = None
    median_patients_per_provider: Optional[float] = None
    mean_patients_per_provider: Optional[float] = None
    gap_ratio: Optional[float] = None
    access_gap_level: Optional[str] = None
    gap_score: Optional[float] = None
    uc05_key: Optional[str] = None
    disease: Optional[str] = None


class PaginatedAccessGapResponse(BaseModel):
    total: int = Field(..., description="Total count of matching records")
    page: int = Field(1, description="Current page number")
    page_size: int = Field(20, description="Number of items per page")
    total_pages: int = Field(1, description="Total number of pages")
    results: List[AccessGapItem] = Field(default_factory=list, description="Access gap records")


class RecommendationItem(BaseModel):
    rank: int = Field(..., description="Rank in priority list")
    areaId: str = Field(..., description="County FIPS or Area identifier")
    areaName: str = Field(..., description="County or City name")
    state: str = Field(..., description="State name or code")
    specialty: str = Field(..., description="Medical specialty")
    disease: Optional[str] = Field(None, description="Related disease")
    riskScore: float = Field(..., description="Risk score percentage (0-100)")
    currentProviders: int = Field(..., description="Current count of providers")
    providersNeeded: int = Field(..., description="Recommended additional providers needed")
    demand: Literal["low", "medium", "high"] = Field("medium", description="Demand pressure level")
    avgTravelDistanceKm: float = Field(..., description="Estimated average travel distance to specialist")
    expectedImpact: Literal["low", "medium", "high"] = Field("medium", description="Expected impact tier")
    expectedImpactScore: float = Field(..., description="Calculated expected impact score (0-100)")
    confidenceScore: Optional[float] = Field(None, description="Model confidence score")
    reason: Optional[str] = Field(None, description="Explanation for recommendation")


class RecommendationSummaryResponse(BaseModel):
    criticalRecruitmentAreas: int = Field(..., description="Count of critical priority recruitment areas")
    totalProvidersRecommended: int = Field(..., description="Total providers recommended across all areas")
    highestRiskPct: float = Field(..., description="Highest risk percentage in network")
    potentialAccessImprovementPct: float = Field(..., description="Projected network access improvement")


class RecommendationsDataResponse(BaseModel):
    summary: RecommendationSummaryResponse
    items: List[RecommendationItem]
