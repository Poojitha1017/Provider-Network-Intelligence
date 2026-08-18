// ---------------------------------------------------------------------------
// Mock data layer for Provider Network Intelligence.
//
// This is the ONLY place raw demo data lives. Pages/components must never
// hard-code area (county) records — they should import from here (or later,
// from src/services/api.ts once a real backend exists). This keeps the UI
// fully decoupled from the shape of any particular dataset.
//
// SCOPE: this build is scoped to Texas, Michigan, and North Carolina only
// (see STATES below) — no other states/countries are represented.
//
// PLACEHOLDER DATA NOTICE: the per-disease breakdown generated in
// buildDiseaseMetrics() below is deterministic placeholder data derived from
// each county's headline risk score — it is NOT the real disease/specialty
// dataset. Swap AREA_SEEDS (and buildDiseaseMetrics, if the real dataset
// carries genuine per-disease numbers) for the real dataset when it is
// provided, keeping the Area/DiseaseMetric shape in src/types intact so no
// UI code needs to change.
// ---------------------------------------------------------------------------

import type {
  Area,
  DashboardMetrics,
  Disease,
  DiseaseMetric,
  Recommendation,
  RecommendationSummary,
  RiskDistributionSlice,
  RiskLevel,
  Specialty,
  SpecialtyGapDatum,
  TrendPoint,
} from "../types";

// ---- lookups ---------------------------------------------------------------

export const SPECIALTIES: Specialty[] = [
  "Cardiology",
  "Endocrinology",
  "Oncology",
  "Neurology",
  "Psychiatry",
  "Pulmonary",
  "Rheumatology",
];

export const DISEASES: Disease[] = [
  "Heart Disease",
  "Diabetes",
  "Cancer",
  "Neurological Disorders",
  "Mental Health Disorders",
  "Respiratory Disease",
  "Arthritis",
];

// Dataset is scoped to these three states only.
export const STATES = ["Texas", "Michigan", "North Carolina"];

function riskLevelFromScore(score: number): RiskLevel {
  if (score >= 85) return "critical";
  if (score >= 65) return "high";
  if (score >= 40) return "medium";
  return "low";
}

function demandLevelFromScore(score: number): "low" | "medium" | "high" {
  if (score >= 70) return "high";
  if (score >= 45) return "medium";
  return "low";
}

// Small deterministic string hash so placeholder per-disease figures are
// stable across renders/reloads instead of using Math.random().
function hashString(input: string): number {
  let h = 0;
  for (let i = 0; i < input.length; i++) {
    h = (h * 31 + input.charCodeAt(i)) >>> 0;
  }
  return h;
}

// ---- raw area (county) seed data --------------------------------------------
// Coordinates are approximate real-world locations so the map reads as
// geographically plausible. All names, populations, and scores are fictional
// placeholders pending the real dataset.

interface AreaSeed {
  id?: string;
  county_fips: string;
  name: string;
  state: string;
  lat: number;
  lng: number;
  population: number;
  specialty: Specialty;
  supply: number;
  riskScore: number;
  travelKm: number;
}

const AREA_SEEDS: AreaSeed[] = [
  { county_fips: "26007", name: "Alpena", state: "Michigan", lat: 45.06, lng: -83.43, population: 26937, specialty: "Cardiology", supply: 5, riskScore: 31, travelKm: 20.7 },
  { county_fips: "26059", name: "Hillsdale", state: "Michigan", lat: 41.92, lng: -84.63, population: 6068, specialty: "Endocrinology", supply: 5, riskScore: 30, travelKm: 6.7 },
  { county_fips: "26063", name: "Pigeon", state: "Michigan", lat: 43.83, lng: -83.27, population: 33970, specialty: "Oncology", supply: 5, riskScore: 94, travelKm: 23.6 },
  { county_fips: "26009", name: "Bellaire", state: "Michigan", lat: 44.98, lng: -85.2, population: 6100, specialty: "Neurology", supply: 3, riskScore: 43, travelKm: 9.0 },
  { county_fips: "26069", name: "Oscoda", state: "Michigan", lat: 44.43, lng: -83.32, population: 26083, specialty: "Psychiatry", supply: 1, riskScore: 45, travelKm: 11.9 },
  { county_fips: "26109", name: "Daggett", state: "Michigan", lat: 45.47, lng: -87.61, population: 34801, specialty: "Pulmonary", supply: 1, riskScore: 54, travelKm: 37.5 },
  { county_fips: "26001", name: "Harrisville", state: "Michigan", lat: 44.65, lng: -83.29, population: 4775, specialty: "Rheumatology", supply: 1, riskScore: 58, travelKm: 36.1 },
  { county_fips: "26079", name: "Kalkaska", state: "Michigan", lat: 44.73, lng: -85.18, population: 13222, specialty: "Cardiology", supply: 5, riskScore: 59, travelKm: 28.4 },
  { county_fips: "37191", name: "Goldsboro", state: "North Carolina", lat: 35.38, lng: -77.99, population: 15589, specialty: "Endocrinology", supply: 3, riskScore: 79, travelKm: 27.0 },
  { county_fips: "37127", name: "Rocky Mount", state: "North Carolina", lat: 35.94, lng: -77.8, population: 40431, specialty: "Oncology", supply: 3, riskScore: 38, travelKm: 19.7 },
  { county_fips: "37069", name: "Louisburg", state: "North Carolina", lat: 36.1, lng: -78.3, population: 41495, specialty: "Neurology", supply: 3, riskScore: 34, travelKm: 35.7 },
  { county_fips: "37161", name: "Rutherfordton", state: "North Carolina", lat: 35.37, lng: -81.96, population: 37163, specialty: "Psychiatry", supply: 1, riskScore: 55, travelKm: 11.1 },
  { county_fips: "37163", name: "Clinton", state: "North Carolina", lat: 35.0, lng: -78.32, population: 14753, specialty: "Pulmonary", supply: 1, riskScore: 46, travelKm: 41.8 },
  { county_fips: "37057", name: "Lexington", state: "North Carolina", lat: 35.82, lng: -80.25, population: 11374, specialty: "Rheumatology", supply: 3, riskScore: 35, travelKm: 19.0 },
  { county_fips: "37189", name: "Boone", state: "North Carolina", lat: 36.22, lng: -81.67, population: 8293, specialty: "Cardiology", supply: 3, riskScore: 51, travelKm: 39.3 },
  { county_fips: "37179", name: "Waxhaw", state: "North Carolina", lat: 34.92, lng: -80.74, population: 32839, specialty: "Endocrinology", supply: 1, riskScore: 75, travelKm: 11.0 },
  { county_fips: "37119", name: "Matthews", state: "North Carolina", lat: 35.12, lng: -80.72, population: 15954, specialty: "Oncology", supply: 5, riskScore: 30, travelKm: 32.6 },
  { county_fips: "37179", name: "Monroe", state: "North Carolina", lat: 34.98, lng: -80.55, population: 22444, specialty: "Neurology", supply: 4, riskScore: 64, travelKm: 35.3 },
  { county_fips: "37123", name: "Troy", state: "North Carolina", lat: 35.36, lng: -79.9, population: 35623, specialty: "Psychiatry", supply: 2, riskScore: 78, travelKm: 23.6 },
  { county_fips: "37085", name: "Dunn", state: "North Carolina", lat: 35.31, lng: -78.61, population: 40314, specialty: "Pulmonary", supply: 1, riskScore: 31, travelKm: 17.5 },
  { county_fips: "37155", name: "Lumberton", state: "North Carolina", lat: 34.62, lng: -79.01, population: 30217, specialty: "Rheumatology", supply: 1, riskScore: 88, travelKm: 11.9 },
  { county_fips: "37013", name: "Washington", state: "North Carolina", lat: 35.55, lng: -77.05, population: 23471, specialty: "Cardiology", supply: 3, riskScore: 75, travelKm: 21.8 },
  { county_fips: "37027", name: "Lenoir", state: "North Carolina", lat: 35.91, lng: -81.54, population: 20724, specialty: "Endocrinology", supply: 5, riskScore: 33, travelKm: 15.4 },
  { county_fips: "37047", name: "Whiteville", state: "North Carolina", lat: 34.33, lng: -78.7, population: 7059, specialty: "Oncology", supply: 1, riskScore: 60, travelKm: 18.2 },
  { county_fips: "37145", name: "Roxboro", state: "North Carolina", lat: 36.39, lng: -78.98, population: 20654, specialty: "Neurology", supply: 2, riskScore: 76, travelKm: 24.1 },
  { county_fips: "37149", name: "Saluda", state: "North Carolina", lat: 35.23, lng: -82.34, population: 22869, specialty: "Psychiatry", supply: 1, riskScore: 92, travelKm: 39.2 },
  { county_fips: "37131", name: "Jackson", state: "North Carolina", lat: 36.39, lng: -77.42, population: 12758, specialty: "Pulmonary", supply: 4, riskScore: 42, travelKm: 31.0 },
  { county_fips: "37041", name: "Edenton", state: "North Carolina", lat: 36.06, lng: -76.61, population: 40293, specialty: "Rheumatology", supply: 3, riskScore: 91, travelKm: 29.5 },
  { county_fips: "37103", name: "Pollocksville", state: "North Carolina", lat: 35.0, lng: -77.22, population: 16792, specialty: "Cardiology", supply: 5, riskScore: 52, travelKm: 35.7 },
  { county_fips: "37033", name: "Yanceyville", state: "North Carolina", lat: 36.4, lng: -79.33, population: 26138, specialty: "Endocrinology", supply: 5, riskScore: 70, travelKm: 38.0 },
  { county_fips: "48027", name: "Harker Heights", state: "Texas", lat: 31.06, lng: -97.66, population: 31030, specialty: "Oncology", supply: 2, riskScore: 57, travelKm: 7.9 },
  { county_fips: "48027", name: "Belton", state: "Texas", lat: 31.06, lng: -97.46, population: 35328, specialty: "Neurology", supply: 1, riskScore: 50, travelKm: 6.0 },
  { county_fips: "48479", name: "Laredo", state: "Texas", lat: 27.51, lng: -99.51, population: 9220, specialty: "Psychiatry", supply: 2, riskScore: 59, travelKm: 13.4 },
  { county_fips: "48213", name: "Gun Barrel City", state: "Texas", lat: 32.33, lng: -96.15, population: 30392, specialty: "Pulmonary", supply: 3, riskScore: 44, travelKm: 41.3 },
  { county_fips: "48367", name: "Willow Park", state: "Texas", lat: 32.79, lng: -97.65, population: 29924, specialty: "Rheumatology", supply: 1, riskScore: 32, travelKm: 30.3 },
  { county_fips: "48367", name: "Weatherford", state: "Texas", lat: 32.76, lng: -97.8, population: 28011, specialty: "Cardiology", supply: 3, riskScore: 65, travelKm: 23.4 },
  { county_fips: "48181", name: "Sherman", state: "Texas", lat: 33.64, lng: -96.61, population: 41539, specialty: "Endocrinology", supply: 1, riskScore: 41, travelKm: 33.2 },
  { county_fips: "48203", name: "Marshall", state: "Texas", lat: 32.54, lng: -94.37, population: 41953, specialty: "Oncology", supply: 3, riskScore: 32, travelKm: 23.0 },
  { county_fips: "48221", name: "Granbury", state: "Texas", lat: 32.44, lng: -97.79, population: 26377, specialty: "Neurology", supply: 1, riskScore: 80, travelKm: 9.4 },
  { county_fips: "48283", name: "Three Rivers", state: "Texas", lat: 28.46, lng: -98.18, population: 39940, specialty: "Psychiatry", supply: 4, riskScore: 33, travelKm: 30.8 },
  { county_fips: "48349", name: "Corsicana", state: "Texas", lat: 32.1, lng: -96.47, population: 8742, specialty: "Pulmonary", supply: 2, riskScore: 34, travelKm: 12.8 },
  { county_fips: "48397", name: "Rockwall", state: "Texas", lat: 32.93, lng: -96.46, population: 18586, specialty: "Rheumatology", supply: 5, riskScore: 73, travelKm: 28.4 },
  { county_fips: "48231", name: "Greenville", state: "Texas", lat: 33.14, lng: -96.11, population: 31845, specialty: "Cardiology", supply: 2, riskScore: 91, travelKm: 13.4 },
  { county_fips: "48493", name: "Floresville", state: "Texas", lat: 29.13, lng: -98.16, population: 22222, specialty: "Endocrinology", supply: 2, riskScore: 83, travelKm: 17.5 },
  { county_fips: "48013", name: "Jourdanton", state: "Texas", lat: 28.91, lng: -98.55, population: 33596, specialty: "Oncology", supply: 1, riskScore: 54, travelKm: 28.0 },
  { county_fips: "48291", name: "Cleveland", state: "Texas", lat: 30.34, lng: -95.09, population: 5852, specialty: "Neurology", supply: 1, riskScore: 31, travelKm: 26.7 },
  { county_fips: "48157", name: "Fulshear", state: "Texas", lat: 29.69, lng: -95.89, population: 16836, specialty: "Psychiatry", supply: 4, riskScore: 78, travelKm: 21.3 },
  { county_fips: "48259", name: "Boerne", state: "Texas", lat: 29.79, lng: -98.73, population: 32718, specialty: "Pulmonary", supply: 5, riskScore: 65, travelKm: 30.5 },
  { county_fips: "48097", name: "Gainesville", state: "Texas", lat: 33.63, lng: -97.13, population: 25041, specialty: "Rheumatology", supply: 4, riskScore: 67, travelKm: 32.4 },
  { county_fips: "48091", name: "Canyon Lake", state: "Texas", lat: 29.87, lng: -98.26, population: 30435, specialty: "Cardiology", supply: 2, riskScore: 72, travelKm: 30.4 },
  { county_fips: "48249", name: "Alice", state: "Texas", lat: 27.75, lng: -98.07, population: 22045, specialty: "Endocrinology", supply: 4, riskScore: 28, travelKm: 12.2 },
  { county_fips: "48419", name: "Tenaha", state: "Texas", lat: 31.95, lng: -94.24, population: 13403, specialty: "Oncology", supply: 2, riskScore: 35, travelKm: 6.1 },
  { county_fips: "48035", name: "Clifton", state: "Texas", lat: 31.78, lng: -97.58, population: 30636, specialty: "Neurology", supply: 5, riskScore: 83, travelKm: 29.2 },
  { county_fips: "48177", name: "Gonzales", state: "Texas", lat: 29.5, lng: -97.45, population: 26915, specialty: "Psychiatry", supply: 3, riskScore: 41, travelKm: 33.0 },
  { county_fips: "48321", name: "Bay City", state: "Texas", lat: 28.98, lng: -95.97, population: 37893, specialty: "Pulmonary", supply: 3, riskScore: 55, travelKm: 41.4 },
  { county_fips: "48371", name: "Fort Stockton", state: "Texas", lat: 30.89, lng: -102.88, population: 7256, specialty: "Rheumatology", supply: 3, riskScore: 84, travelKm: 10.0 },
  { county_fips: "48179", name: "Pampa", state: "Texas", lat: 35.53, lng: -100.96, population: 19770, specialty: "Cardiology", supply: 2, riskScore: 48, travelKm: 41.3 },
  { county_fips: "48089", name: "Columbus", state: "Texas", lat: 29.71, lng: -96.55, population: 5102, specialty: "Endocrinology", supply: 5, riskScore: 80, travelKm: 24.7 },
  { county_fips: "48477", name: "Brenham", state: "Texas", lat: 30.17, lng: -96.4, population: 20830, specialty: "Oncology", supply: 5, riskScore: 54, travelKm: 18.0 },
];

// Builds the full per-disease breakdown for a county. The county's
// "headline" specialty/disease pairing carries the county's real risk score
// and provider count; the remaining diseases get deterministic, clearly
// secondary placeholder figures until the real dataset is wired in.
function buildDiseaseMetrics(seed: AreaSeed): DiseaseMetric[] {
  const primaryDisease = SPECIALTY_TO_DISEASE[seed.specialty];

  return DISEASES.map((disease) => {
    if (disease === primaryDisease) {
      return {
        disease,
        riskScore: seed.riskScore,
        providerSupply: seed.supply,
        demandLevel: demandLevelFromScore(seed.riskScore),
      };
    }

    const seedNum = hashString(`${seed.name}-${seed.state}-${disease}`);
    const jitter = (seedNum % 21) - 10; // -10..10, deterministic per county+disease
    const riskScore = Math.max(5, Math.min(95, Math.round(seed.riskScore * 0.55 + jitter)));
    const providerSupply = Math.max(0, Math.round(seed.supply * 0.4 + ((seedNum >> 4) % 3) - 1));

    return {
      disease,
      riskScore,
      providerSupply,
      demandLevel: demandLevelFromScore(riskScore),
    };
  });
}

const SPECIALTY_TO_DISEASE: Record<Specialty, Disease> = {
  Cardiology: "Heart Disease",
  Endocrinology: "Diabetes",
  Oncology: "Cancer",
  Neurology: "Neurological Disorders",
  Psychiatry: "Mental Health Disorders",
  Pulmonary: "Respiratory Disease",
  Rheumatology: "Arthritis",
};

function seedToArea(seed: AreaSeed, index: number): Area {
  const id = `area-${index + 1}`;
  const riskLevel = riskLevelFromScore(seed.riskScore);
  const populationFactor = seed.population / 100000;
  const supplyGap = Math.max(0, 5 - seed.supply);
  // A county with no supply gap needs 0 additional providers — previously
  // this was floored at 1 for every county (even fully-staffed ones),
  // which fed incorrect values into the Priority Table's "Providers Needed"
  // and "Expected Impact" columns.
  const providersNeeded =
    supplyGap === 0 ? 0 : Math.max(1, Math.round(supplyGap * (0.6 + populationFactor * 0.15)));

  const demandPressure = Math.min(100, Math.round(seed.riskScore * 0.95 + populationFactor));
  const providerShortage = Math.min(100, Math.round((5 - seed.supply) * 20 + 5));
  const travelDistanceFactor = Math.min(100, Math.round(seed.travelKm * 2.4));
  const utilization = Math.min(100, Math.round(seed.riskScore * 0.8 + supplyGap * 3));

  const networkAdequacyPct = Math.max(5, Math.min(95, Math.round(100 - seed.riskScore * 0.65)));

  const demandLevel = demandLevelFromScore(seed.riskScore);

  return {
    id,
    county_fips: seed.county_fips,
    name: seed.name,
    state: seed.state,
    latitude: seed.lat,
    longitude: seed.lng,
    population: seed.population,
    primarySpecialty: seed.specialty,
    diseases: buildDiseaseMetrics(seed),
    providerSupply: seed.supply,
    demandLevel,
    riskScore: seed.riskScore,
    riskLevel,
    accessGap: riskLevel,
    avgTravelDistanceKm: seed.travelKm,
    networkAdequacyPct,
    providersNeeded,
    recommendationConfidencePct: Math.min(97, Math.round(seed.riskScore * 1.0 + 4)),
    // expectedImpact / expectedImpactScore are filled in below, once we know
    // the dataset-wide maxima needed to normalize the formula.
    expectedImpact: "low",
    expectedImpactScore: 0,
    riskFactors: {
      demandPressure,
      providerShortage,
      travelDistance: travelDistanceFactor,
      utilization,
    },
    lastUpdated: "2026-07-31",
  };
}

// ---- Expected Impact formula -------------------------------------------------
// The Priority Table ranks counties by "expected impact" rather than raw risk
// score alone. Expected impact blends:
//   - riskScore (40%)       how underserved the county already is
//   - needScore (30%)       how large a fix is being recommended, relative
//                            to the largest recommendation in the dataset
//   - populationScore (20%) how many people stand to benefit, relative to
//                            the most populous county in the dataset
//   - adequacyGapScore (10%) how far below network adequacy the county sits
// All four sub-scores are 0-100, so the weighted result is naturally 0-100.
function applyExpectedImpact(areas: Area[]): Area[] {
  const maxPopulation = Math.max(...areas.map((a) => a.population));
  const maxProvidersNeeded = Math.max(1, ...areas.map((a) => a.providersNeeded));

  return areas.map((area) => {
    const populationScore = (area.population / maxPopulation) * 100;
    const needScore = (area.providersNeeded / maxProvidersNeeded) * 100;
    const adequacyGapScore = 100 - area.networkAdequacyPct;

    const expectedImpactScore = Math.round(
      area.riskScore * 0.4 + needScore * 0.3 + populationScore * 0.2 + adequacyGapScore * 0.1
    );

    const expectedImpact = expectedImpactScore >= 70 ? "high" : expectedImpactScore >= 40 ? "medium" : "low";

    return { ...area, expectedImpactScore, expectedImpact };
  });
}

export const AREAS: Area[] = applyExpectedImpact(AREA_SEEDS.map(seedToArea));

export function getAreaById(id: string): Area | undefined {
  return AREAS.find((a) => a.id === id);
}

export function getAreaByName(name: string): Area | undefined {
  return AREAS.find((a) => a.name === name);
}

// ---- dashboard aggregates ----------------------------------------------------

export const DASHBOARD_METRICS: DashboardMetrics = {
  totalAreas: 59,
  totalAreasTrendPct: 3.1,
  totalProviders: 167,
  totalProvidersTrendPct: 4.6,
  highRiskAreas: 22,
  highRiskAreasTrendPct: 12,
  accessGapAreas: 44,
  accessGapAreasTrendPct: 6.8,
  avgTravelDistanceKm: 23.4,
  avgTravelDistanceTrendPct: -2.4,
};

export const RISK_DISTRIBUTION: RiskDistributionSlice[] = [
  { level: "low", label: "Low", areaCount: 15 },
  { level: "medium", label: "Medium", areaCount: 22 },
  { level: "high", label: "High", areaCount: 17 },
  { level: "critical", label: "Critical", areaCount: 5 },
];

export const SPECIALTY_GAPS: SpecialtyGapDatum[] = [
  { specialty: "Cardiology", areasWithGap: 8 },
  { specialty: "Psychiatry", areasWithGap: 7 },
  { specialty: "Neurology", areasWithGap: 6 },
  { specialty: "Pulmonary", areasWithGap: 6 },
  { specialty: "Rheumatology", areasWithGap: 6 },
  { specialty: "Endocrinology", areasWithGap: 6 },
  { specialty: "Oncology", areasWithGap: 5 },
];

export const ACCESS_GAP_TREND: TrendPoint[] = [
  { month: "Jan", accessGapAreas: 36 },
  { month: "Feb", accessGapAreas: 38 },
  { month: "Mar", accessGapAreas: 39 },
  { month: "Apr", accessGapAreas: 41 },
  { month: "May", accessGapAreas: 40 },
  { month: "Jun", accessGapAreas: 42 },
  { month: "Jul", accessGapAreas: 44 },
];

// Top critical areas for dashboard table — top N by riskScore.
export function getTopCriticalAreas(count = 5): Area[] {
  return [...AREAS].sort((a, b) => b.riskScore - a.riskScore).slice(0, count);
}

// ---- recommendations ----------------------------------------------------
// Ranked by expectedImpactScore (see applyExpectedImpact above), not raw
// risk score — this is the Priority Table's ranking formula.
export function getRecommendations(): Recommendation[] {
  return [...AREAS]
    .sort((a, b) => b.expectedImpactScore - a.expectedImpactScore)
    .map((area, i) => ({
      rank: i + 1,
      areaId: area.id,
      areaName: area.name,
      state: area.state,
      specialty: area.primarySpecialty,
      riskScore: area.riskScore,
      currentProviders: area.providerSupply,
      providersNeeded: area.providersNeeded,
      demand: area.demandLevel,
      avgTravelDistanceKm: area.avgTravelDistanceKm,
      expectedImpact: area.expectedImpact,
      expectedImpactScore: area.expectedImpactScore,
    }));
}

// Recommendation summary is derived directly from getRecommendations()/AREAS
// rather than hand-maintained, so it can never drift out of sync with the
// Priority Table's own numbers (previously the static summary numbers did
// not match what the table's own formula produced).
export function getRecommendationSummary(): RecommendationSummary {
  const recs = getRecommendations();
  const criticalRecruitmentAreas = recs.filter((r) => r.expectedImpact === "high").length;
  const totalProvidersRecommended = recs.reduce((sum, r) => sum + r.providersNeeded, 0);
  const highestRiskPct = recs.length ? Math.max(...recs.map((r) => r.riskScore)) : 0;

  const improvementSum = recs.reduce((sum, r) => {
    if (r.providersNeeded === 0) return sum;
    const sim = computeWhatIf(r.areaId, r.specialty, Math.min(5, r.providersNeeded));
    return sum + (sim ? sim.accessImprovementPct : 0);
  }, 0);
  const potentialAccessImprovementPct = recs.length ? Math.round(improvementSum / recs.length) : 0;

  return {
    criticalRecruitmentAreas,
    totalProvidersRecommended,
    highestRiskPct,
    potentialAccessImprovementPct,
  };
}

// ---- what-if simulator ----------------------------------------------------

export function computeWhatIf(areaId: string, specialty: Specialty, providersToAdd: number) {
  const area = getAreaById(areaId);
  if (!area) return null;

  const currentRisk = area.riskScore;

  // Simple mock decay formula: each added provider reduces risk with
  // diminishing returns, floor of ~12 (never fully "solved" by this alone).
  const riskAt = (added: number) => {
    const decay = 1 - Math.exp(-added * 0.42);
    const reduction = (currentRisk - 12) * decay;
    return Math.max(12, Math.round(currentRisk - reduction));
  };

  const predictedRisk = riskAt(providersToAdd);
  const accessImprovementPct = Math.round(((currentRisk - predictedRisk) / currentRisk) * 100);
  const newProviderCount = area.providerSupply + providersToAdd;
  const predictedAccessGap = riskLevelFromScore(predictedRisk);
  const expectedImpact: "low" | "medium" | "high" =
    accessImprovementPct >= 40 ? "high" : accessImprovementPct >= 18 ? "medium" : "low";

  const curve = [0, 1, 2, 3, 4, 5].map((n) => ({
    providersAdded: n,
    predictedRiskScore: riskAt(n),
  }));

  return {
    areaId: area.id,
    areaName: area.name,
    state: area.state,
    specialty,
    currentProviders: area.providerSupply,
    providersToAdd,
    newProviderCount,
    currentRiskScore: currentRisk,
    predictedRiskScore: predictedRisk,
    accessImprovementPct,
    predictedAccessGap,
    expectedImpact,
    curve,
  };
}
