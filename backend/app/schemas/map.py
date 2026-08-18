from typing import List, Optional, Literal, Dict, Any
from pydantic import BaseModel, Field


class DiseaseMetric(BaseModel):
    disease: str
    riskScore: float
    providerSupply: int
    demandLevel: Literal["low", "medium", "high"] = "medium"


class RiskFactors(BaseModel):
    demandPressure: float = 50.0
    providerShortage: float = 50.0
    travelDistance: float = 50.0
    utilization: float = 50.0


class MapAreaItem(BaseModel):
    id: str = Field(..., description="Unique Area ID / County FIPS")
    county_fips: str = Field(..., description="County FIPS code")
    name: str = Field(..., description="County or City Name")
    state: str = Field(..., description="State name or code")
    latitude: float = Field(..., description="Geographic Latitude")
    longitude: float = Field(..., description="Geographic Longitude")
    population: int = Field(..., description="Estimated population or beneficiaries")
    primarySpecialty: str = Field(..., description="Primary specialty evaluated")
    providerSupply: int = Field(..., description="Total active in-network provider count")
    demandLevel: Literal["low", "medium", "high"] = "medium"
    riskScore: float = Field(..., description="Calculated risk score (0-100)")
    riskLevel: Literal["low", "medium", "high", "critical"] = "medium"
    accessGap: Literal["low", "medium", "high", "critical"] = "medium"
    avgTravelDistanceKm: float = Field(20.0, description="Average travel distance in km")
    networkAdequacyPct: float = Field(65.0, description="Network adequacy percentage")
    providersNeeded: int = Field(0, description="Estimated providers needed")
    recommendationConfidencePct: float = Field(80.0, description="Recommendation confidence percentage")
    expectedImpact: Literal["low", "medium", "high"] = "medium"
    expectedImpactScore: float = Field(50.0, description="Expected impact score")
    riskFactors: RiskFactors = Field(default_factory=RiskFactors)
    diseases: List[DiseaseMetric] = Field(default_factory=list, description="Per-disease breakdown for this area")
    lastUpdated: str = Field("2026-08-18", description="Date last calculated")


class MapAreasResponse(BaseModel):
    total: int
    areas: List[MapAreaItem]
