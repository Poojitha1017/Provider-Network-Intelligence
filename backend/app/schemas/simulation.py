from typing import List, Optional, Literal
from pydantic import BaseModel, Field


class WhatIfRequest(BaseModel):
    county_fips: Optional[str] = Field(None, description="County FIPS Code (e.g. '48183')")
    areaId: Optional[str] = Field(None, description="Area ID or County FIPS")
    specialty: str = Field(..., description="Target specialty (e.g. 'Endocrinology')")
    disease: Optional[str] = Field(None, description="Target disease (e.g. 'Diabetes')")
    additional_providers: Optional[int] = Field(None, ge=0, le=20, description="Additional providers to add")
    providersToAdd: Optional[int] = Field(None, ge=0, le=20, description="Additional providers to add (UI alias)")


class WhatIfCurvePoint(BaseModel):
    providersAdded: int
    predictedRiskScore: float


class WhatIfCurrent(BaseModel):
    provider_count: int
    estimated_patients: int
    patients_per_provider: float
    gap_score: float
    access_gap_level: str


class WhatIfProjection(BaseModel):
    additional_providers: int
    projected_provider_count: int
    projected_patients_per_provider: float
    projected_gap_score: float
    projected_access_gap_level: str
    access_improvement_pct: float
    expected_impact: Literal["low", "medium", "high"]


class WhatIfResponse(BaseModel):
    county_fips: str
    areaId: str
    areaName: str
    state: str
    specialty: str
    disease: Optional[str] = None
    
    # Detailed nested shapes
    current: WhatIfCurrent
    simulation: WhatIfProjection

    # Direct UI-convenience fields (matching React WhatIfResult type)
    currentProviders: int
    providersToAdd: int
    newProviderCount: int
    currentRiskScore: float
    predictedRiskScore: float
    accessImprovementPct: float
    predictedAccessGap: str
    expectedImpact: Literal["low", "medium", "high"]
    curve: List[WhatIfCurvePoint]
