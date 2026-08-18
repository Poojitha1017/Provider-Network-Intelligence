import type {
  Area,
  DashboardMetrics,
  Recommendation,
  RecommendationSummary,
  RiskDistributionSlice,
  Specialty,
  SpecialtyGapDatum,
  TrendPoint,
  WhatIfResult,
} from "../types";

export const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000/api/v1";

function getToken(): string | null {
  try {
    return localStorage.getItem("pni_token");
  } catch {
    return null;
  }
}

function getHeaders(): HeadersInit {
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
  };
  const token = getToken();
  if (token) {
    headers["Authorization"] = `Bearer ${token}`;
  }
  return headers;
}

// ---------------------------------------------------------------------------
// Dynamic Filter Options
// ---------------------------------------------------------------------------
export interface FilterOptionsData {
  states: string[];
  cities: string[];
  county_fips_list: string[];
  counties: { county_fips: string; county_name?: string; state?: string }[];
  diseases: string[];
  specialties: string[];
  risk_levels: string[];
}

export async function getFilterOptions(params?: {
  county_fips?: string;
  city?: string;
  disease?: string;
  specialty?: string;
  risk_level?: string;
  state?: string;
}): Promise<FilterOptionsData> {
  const query = new URLSearchParams();
  if (params?.county_fips && params.county_fips !== "All Counties") query.set("county_fips", params.county_fips);
  if (params?.city && params.city !== "All Cities") query.set("city", params.city);
  if (params?.disease && params.disease !== "All Diseases") query.set("disease", params.disease);
  if (params?.specialty && params.specialty !== "All Specialties") query.set("specialty", params.specialty);
  if (params?.risk_level && params.risk_level !== "All") query.set("risk_level", params.risk_level);
  if (params?.state && params.state !== "All States") query.set("state", params.state);

  const url = `${API_BASE_URL}/filters/options${query.toString() ? `?${query.toString()}` : ""}`;
  const res = await fetch(url, { headers: getHeaders() });
  if (!res.ok) {
    throw new Error(`Failed to load filter options: ${res.statusText}`);
  }
  return res.json();
}

// ---------------------------------------------------------------------------
// Dashboard Overview
// ---------------------------------------------------------------------------
export async function getDashboardData(): Promise<{
  metrics: DashboardMetrics;
  riskDistribution: RiskDistributionSlice[];
  specialtyGaps: SpecialtyGapDatum[];
  trend: TrendPoint[];
  topCriticalAreas: Area[];
}> {
  const res = await fetch(`${API_BASE_URL}/dashboard/summary`, {
    headers: getHeaders(),
  });
  if (!res.ok) {
    throw new Error(`Failed to load dashboard summary: ${res.statusText}`);
  }
  const data = await res.json();
  return {
    metrics: data.metrics,
    riskDistribution: data.riskDistribution,
    specialtyGaps: data.specialtyGaps,
    trend: data.trend,
    topCriticalAreas: data.topCriticalAreas as Area[],
  };
}

// ---------------------------------------------------------------------------
// Map & Area Insights
// ---------------------------------------------------------------------------
export async function getAreas(filters?: {
  state?: string;
  county?: string;
  specialty?: string;
  riskLevel?: string;
}): Promise<Area[]> {
  const query = new URLSearchParams();
  if (filters?.state && filters.state !== "All States") query.set("state", filters.state);
  if (filters?.county && filters.county !== "All Counties") query.set("county_fips", filters.county);
  if (filters?.specialty && filters.specialty !== "All Specialties") query.set("specialty", filters.specialty);
  if (filters?.riskLevel && filters.riskLevel !== "All") query.set("risk_level", filters.riskLevel);

  const url = `${API_BASE_URL}/map/areas${query.toString() ? `?${query.toString()}` : ""}`;
  const res = await fetch(url, { headers: getHeaders() });
  if (!res.ok) {
    throw new Error(`Failed to load map areas: ${res.statusText}`);
  }
  const data = await res.json();
  return data.areas as Area[];
}

export async function getAreaDetails(areaId: string): Promise<Area | null> {
  const areas = await getAreas({ county: areaId });
  if (areas && areas.length > 0) {
    const match = areas.find((a) => a.id === areaId || a.name.toLowerCase() === areaId.toLowerCase());
    return match ?? areas[0];
  }
  // Fallback query all
  const all = await getAreas();
  return all.find((a) => a.id === areaId || a.name.toLowerCase() === areaId.toLowerCase()) ?? null;
}

// ---------------------------------------------------------------------------
// Recommendations
// ---------------------------------------------------------------------------
export async function getRecommendationsData(filters?: {
  state?: string;
  specialty?: string;
  riskLevel?: string;
}): Promise<{
  summary: RecommendationSummary;
  items: Recommendation[];
}> {
  const query = new URLSearchParams();
  if (filters?.state && filters.state !== "All States") query.set("state", filters.state);
  if (filters?.specialty && filters.specialty !== "All Specialties") query.set("specialty", filters.specialty);
  if (filters?.riskLevel && filters.riskLevel !== "All") query.set("risk_level", filters.riskLevel);

  const url = `${API_BASE_URL}/recommendations${query.toString() ? `?${query.toString()}` : ""}`;
  const res = await fetch(url, { headers: getHeaders() });
  if (!res.ok) {
    throw new Error(`Failed to load recommendations: ${res.statusText}`);
  }
  const data = await res.json();
  return {
    summary: data.summary,
    items: data.items,
  };
}

// ---------------------------------------------------------------------------
// What-If Simulation
// ---------------------------------------------------------------------------
export async function getWhatIfPrediction(
  areaId: string,
  specialty: Specialty | string,
  providersAdded: number
): Promise<WhatIfResult | null> {
  const payload = {
    county_fips: areaId,
    areaId: areaId,
    specialty: specialty,
    additional_providers: providersAdded,
    providersToAdd: providersAdded,
  };

  const res = await fetch(`${API_BASE_URL}/simulation/what-if`, {
    method: "POST",
    headers: getHeaders(),
    body: JSON.stringify(payload),
  });

  if (!res.ok) {
    throw new Error(`Failed to calculate what-if prediction: ${res.statusText}`);
  }
  const data = await res.json();
  return data as WhatIfResult;
}

// ---------------------------------------------------------------------------
// Search & Providers
// ---------------------------------------------------------------------------
export async function searchIntelligence(params: {
  county_fips?: string;
  state?: string;
  city?: string;
  disease?: string;
  specialty?: string;
  risk_level?: string;
  page?: number;
  page_size?: number;
}) {
  const query = new URLSearchParams();
  Object.entries(params).forEach(([k, v]) => {
    if (v !== undefined && v !== null && v !== "" && !String(v).startsWith("All")) {
      query.set(k, String(v));
    }
  });
  const res = await fetch(`${API_BASE_URL}/search?${query.toString()}`, {
    headers: getHeaders(),
  });
  if (!res.ok) throw new Error("Search failed");
  return res.json();
}

export async function getProvidersApi(params: {
  county_fips?: string;
  state?: string;
  city?: string;
  specialty?: string;
  disease?: string;
  telehealth?: boolean;
  page?: number;
  page_size?: number;
}) {
  const query = new URLSearchParams();
  Object.entries(params).forEach(([k, v]) => {
    if (v !== undefined && v !== null && v !== "" && !String(v).startsWith("All")) {
      query.set(k, String(v));
    }
  });
  const res = await fetch(`${API_BASE_URL}/providers?${query.toString()}`, {
    headers: getHeaders(),
  });
  if (!res.ok) throw new Error("Failed to load providers");
  return res.json();
}

// ---------------------------------------------------------------------------
// Auth API Endpoints
// ---------------------------------------------------------------------------
export async function loginApi(email: string, password: string) {
  const res = await fetch(`${API_BASE_URL}/auth/login`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email, password }),
  });
  const data = await res.json();
  if (!res.ok) {
    throw new Error(data.message || data.detail || "Unable to sign in.");
  }
  return data;
}

export async function signupApi(input: {
  fullName: string;
  email: string;
  mobile?: string;
  organization?: string;
  role: string;
  password: string;
}) {
  const res = await fetch(`${API_BASE_URL}/auth/signup`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(input),
  });
  const data = await res.json();
  if (!res.ok) {
    throw new Error(data.message || data.detail || "Unable to create account.");
  }
  return data;
}

export async function forgotPasswordApi(email: string) {
  const res = await fetch(`${API_BASE_URL}/auth/forgot-password`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email }),
  });
  const data = await res.json();
  if (!res.ok) {
    throw new Error(data.message || data.detail || "Unable to send reset email.");
  }
  return data;
}

export async function getMeApi(token: string) {
  const res = await fetch(`${API_BASE_URL}/auth/me`, {
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${token}`,
    },
  });
  if (!res.ok) throw new Error("Session expired");
  return res.json();
}

// ---------------------------------------------------------------------------
// AI Assistant Chat
// ---------------------------------------------------------------------------
export async function sendChatQuery(
  query: string,
  history?: Array<{ role: string; content: string }>,
  context?: Record<string, any>
): Promise<{
  answer: string;
  suggested_actions?: string[];
  data_summary?: Record<string, any>;
  timestamp: string;
}> {
  const res = await fetch(`${API_BASE_URL}/chat/query`, {
    method: "POST",
    headers: getHeaders(),
    body: JSON.stringify({ query, history, context }),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || "Unable to process query at this time.");
  }
  return res.json();
}

