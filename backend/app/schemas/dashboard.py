from typing import List, Optional, Any, Dict
from pydantic import BaseModel, Field


class DashboardMetrics(BaseModel):
    totalAreas: int
    totalAreasTrendPct: float
    totalProviders: int
    totalProvidersTrendPct: float
    highRiskAreas: int
    highRiskAreasTrendPct: float
    accessGapAreas: int
    accessGapAreasTrendPct: float
    avgTravelDistanceKm: float
    avgTravelDistanceTrendPct: float


class RiskDistributionSlice(BaseModel):
    level: str
    label: str
    areaCount: int


class SpecialtyGapDatum(BaseModel):
    specialty: str
    areasWithGap: int


class TrendPoint(BaseModel):
    month: str
    accessGapAreas: int


class DashboardSummaryResponse(BaseModel):
    metrics: DashboardMetrics
    riskDistribution: List[RiskDistributionSlice]
    specialtyGaps: List[SpecialtyGapDatum]
    trend: List[TrendPoint]
    topCriticalAreas: List[Dict[str, Any]]
