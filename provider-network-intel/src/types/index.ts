// ---------------------------------------------------------------------------
// Core domain types for Provider Network Intelligence.
//
// These types are the contract between the UI and the data layer. Pages and
// components are written against these interfaces only — never against raw
// mock-data shapes or (later) raw dataset/API field names. When the real
// FastAPI backend is introduced, it only needs to return objects that satisfy
// these shapes (see src/services/api.ts) and no UI code will need to change.
// ---------------------------------------------------------------------------

export type RiskLevel = "low" | "medium" | "high" | "critical";

export type DemandLevel = "low" | "medium" | "high";

export type ImpactLevel = "low" | "medium" | "high";

export type Specialty =
  | "Cardiology"
  | "Endocrinology"
  | "Oncology"
  | "Neurology"
  | "Psychiatry"
  | "Pulmonary"
  | "Rheumatology";

export type Disease =
  | "Heart Disease"
  | "Diabetes"
  | "Cancer"
  | "Neurological Disorders"
  | "Mental Health Disorders"
  | "Respiratory Disease"
  | "Arthritis";

export interface RiskFactors {
  demandPressure: number; // 0-100
  providerShortage: number; // 0-100
  travelDistance: number; // 0-100
  utilization: number; // 0-100
}

// Per-disease breakdown for a county. Every county tracks all diseases in
// DISEASES — not just one — so the map popup and any future disease-specific
// views can show the full picture for that county rather than a single
// filtered disease.
export interface DiseaseMetric {
  disease: Disease;
  riskScore: number; // 0-100
  providerSupply: number;
  demandLevel: DemandLevel;
}

export interface Area {
  id: string;
  county_fips?: string;
  name: string; // county name
  state: string;
  latitude: number;
  longitude: number;
  population: number;
  primarySpecialty: Specialty;
  diseases: DiseaseMetric[]; // all tracked diseases for this county
  providerSupply: number;
  demandLevel: DemandLevel;
  riskScore: number; // 0-100 — headline risk score for the county
  riskLevel: RiskLevel;
  accessGap: RiskLevel;
  avgTravelDistanceKm: number;
  networkAdequacyPct: number; // 0-100
  providersNeeded: number;
  recommendationConfidencePct: number;
  expectedImpact: ImpactLevel;
  expectedImpactScore: number; // 0-100 — drives Priority Table ranking
  riskFactors: RiskFactors;
  lastUpdated: string;
}

export interface DashboardMetrics {
  totalAreas: number;
  totalAreasTrendPct: number;
  totalProviders: number;
  totalProvidersTrendPct: number;
  highRiskAreas: number;
  highRiskAreasTrendPct: number;
  accessGapAreas: number;
  accessGapAreasTrendPct: number;
  avgTravelDistanceKm: number;
  avgTravelDistanceTrendPct: number;
}

export interface RiskDistributionSlice {
  level: RiskLevel;
  label: string;
  areaCount: number;
}

export interface SpecialtyGapDatum {
  specialty: Specialty;
  areasWithGap: number;
}

export interface TrendPoint {
  month: string;
  accessGapAreas: number;
}

export interface Recommendation {
  rank: number;
  areaId: string;
  areaName: string;
  state: string;
  specialty: Specialty;
  riskScore: number;
  currentProviders: number;
  providersNeeded: number;
  demand: DemandLevel;
  avgTravelDistanceKm: number;
  expectedImpact: ImpactLevel;
  expectedImpactScore: number; // 0-100 — formula-driven ranking value
  disease?: string;
  reason?: string;
  confidenceScore?: number;
}

export interface RecommendationSummary {
  criticalRecruitmentAreas: number;
  totalProvidersRecommended: number;
  highestRiskPct: number;
  potentialAccessImprovementPct: number;
}

export interface WhatIfInput {
  areaId: string;
  specialty: Specialty;
  providersToAdd: number; // 0-5
}

export interface WhatIfResult {
  areaId: string;
  areaName: string;
  state: string;
  specialty: Specialty;
  current: {
    provider_count: number;
    estimated_patients: number;
    patients_per_provider: number;
    gap_score: number;
    access_gap_level: string;
  };
  currentProviders: number;
  providersToAdd: number;
  newProviderCount: number;
  currentRiskScore: number;
  predictedRiskScore: number;
  accessImprovementPct: number;
  predictedAccessGap: RiskLevel;
  expectedImpact: ImpactLevel;
  curve: { providersAdded: number; predictedRiskScore: number }[];
}

export interface FilterState {
  state: string; // "All States" or a state name
  county: string; // "All Counties" or a county name
  specialty: string; // "All Specialties" or a specialty name
  riskLevel: string; // "All" | RiskLevel (capitalized in UI)
}

export interface AuthUser {
  name: string;
  email: string;
  role: string;
}
