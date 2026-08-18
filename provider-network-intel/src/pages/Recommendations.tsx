import { useEffect, useMemo, useState } from "react";
import { useNavigate } from "react-router-dom";
import { ArrowUpDown, Lightbulb, Target, Users2, TrendingUp, Search, X, Phone } from "lucide-react";
import DashboardLayout from "../components/DashboardLayout";
import PageHeader from "../components/PageHeader";
import ChartCard from "../components/ChartCard";
import KpiCard from "../components/KpiCard";
import DataTable, { type DataTableColumn } from "../components/DataTable";
import StatusBadge from "../components/StatusBadge";
import LoadingState from "../components/LoadingState";
import FilterPanel from "../components/FilterPanel";
import TwilioAlertModal from "../components/TwilioAlertModal";
import { getRecommendationsData, getFilterOptions, type FilterOptionsData } from "../services/api";
import { useSelectedArea } from "../context/SelectedAreaContext";
import type { Recommendation, RecommendationSummary } from "../types";
import { STATE_COUNTY_MAP } from "../utils/constants";

type SortKey = "expectedImpactScore" | "riskScore" | "providersNeeded" | "avgTravelDistanceKm";

const IMPACT_TONE = { low: "warning", medium: "warning", high: "positive" } as const;
const DEMAND_TONE = { low: "neutral", medium: "warning", high: "negative" } as const;

interface RecFilters {
  state: string;
  specialty: string;
  riskLevel: string;
}

export default function Recommendations() {
  const navigate = useNavigate();
  const { setSelectedAreaId } = useSelectedArea();

  const [loading, setLoading] = useState(true);
  const [summary, setSummary] = useState<RecommendationSummary | null>(null);
  const [items, setItems] = useState<Recommendation[]>([]);
  const [filterOptions, setFilterOptions] = useState<FilterOptionsData | null>(null);
  const [sortKey, setSortKey] = useState<SortKey>("expectedImpactScore");
  const [sortDir, setSortDir] = useState<"asc" | "desc">("desc");
  const [filters, setFilters] = useState<RecFilters>({
    state: "All States",
    specialty: "All Specialties",
    riskLevel: "All",
  });
  const [twilioModalOpen, setTwilioModalOpen] = useState(false);
  const [selectedRec, setSelectedRec] = useState<Recommendation | null>(null);

  function openTwilioAlert(rec: Recommendation) {
    setSelectedRec(rec);
    setTwilioModalOpen(true);
  }

  // Load filter options
  useEffect(() => {
    getFilterOptions().then((opts) => setFilterOptions(opts)).catch(console.error);
  }, []);

  // Load recommendations
  useEffect(() => {
    let active = true;
    setLoading(true);
    getRecommendationsData({
      state: filters.state,
      specialty: filters.specialty,
      riskLevel: filters.riskLevel,
    })
      .then((data) => {
        if (!active) return;
        setSummary(data.summary);
        setItems(data.items);
        setLoading(false);
      })
      .catch((err) => {
        console.error("Error loading recommendations:", err);
        if (active) setLoading(false);
      });

    return () => {
      active = false;
    };
  }, [filters]);

  const [searchQuery, setSearchQuery] = useState("");

  const filteredSorted = useMemo(() => {
    const rows = [...items].sort((a, b) => (sortDir === "desc" ? b[sortKey] - a[sortKey] : a[sortKey] - b[sortKey]));
    return rows;
  }, [items, sortKey, sortDir]);

  const searchedRows = useMemo(() => {
    if (!searchQuery.trim()) return filteredSorted;
    const q = searchQuery.toLowerCase().trim();
    return filteredSorted.filter(
      (r) =>
        r.areaName.toLowerCase().includes(q) ||
        r.state.toLowerCase().includes(q) ||
        r.specialty.toLowerCase().includes(q) ||
        (r.disease && r.disease.toLowerCase().includes(q)) ||
        (r.reason && r.reason.toLowerCase().includes(q)) ||
        r.expectedImpact.toLowerCase().includes(q)
    );
  }, [filteredSorted, searchQuery]);

  function toggleSort(key: SortKey) {
    if (sortKey === key) {
      setSortDir((d) => (d === "desc" ? "asc" : "desc"));
    } else {
      setSortKey(key);
      setSortDir("desc");
    }
  }

  function goToArea(areaId: string) {
    setSelectedAreaId(areaId);
    navigate("/area-insights");
  }

  function goToSimulate(areaId: string) {
    setSelectedAreaId(areaId);
    navigate("/what-if");
  }

  const sortHeader = (label: string, key: SortKey) => (
    <button onClick={() => toggleSort(key)} className="flex items-center gap-1 hover:text-navy-900">
      {label}
      <ArrowUpDown className="h-3 w-3" />
    </button>
  );

  const columns: DataTableColumn<Recommendation>[] = [
    { key: "rank", header: "Rank", render: (r) => `#${searchedRows.indexOf(r) + 1}`, widthClass: "w-14" },
    { key: "area", header: "County / Area", render: (r) => <span className="font-semibold">{r.areaName}</span> },
    { key: "state", header: "State", render: (r) => r.state },
    { key: "specialty", header: "Specialty", render: (r) => r.specialty },
    { key: "riskScore", header: sortHeader("Risk Score", "riskScore"), render: (r) => `${r.riskScore}%` },
    { key: "currentProviders", header: "Current Providers", render: (r) => r.currentProviders },
    {
      key: "providersNeeded",
      header: sortHeader("Providers Needed", "providersNeeded"),
      render: (r) => <span className="font-semibold">{r.providersNeeded}</span>,
    },
    {
      key: "demand",
      header: "Demand",
      render: (r) => <StatusBadge label={cap(r.demand)} tone={DEMAND_TONE[r.demand]} />,
    },
    {
      key: "travel",
      header: sortHeader("Travel Distance", "avgTravelDistanceKm"),
      render: (r) => `${r.avgTravelDistanceKm} km`,
    },
    {
      key: "impact",
      header: sortHeader("Expected Impact", "expectedImpactScore"),
      render: (r) => (
        <div className="flex items-center gap-2">
          <StatusBadge label={cap(r.expectedImpact)} tone={IMPACT_TONE[r.expectedImpact]} />
          <span className="text-xs text-slate-400">{r.expectedImpactScore}</span>
        </div>
      ),
    },
    {
      key: "action",
      header: "Action",
      align: "right",
      render: (r) => (
        <div className="flex justify-end gap-2">
          <button
            onClick={() => goToArea(r.areaId)}
            className="rounded-md border border-brand-200 px-3 py-1 text-xs font-semibold text-brand-700 hover:bg-brand-50"
          >
            View
          </button>
          <button
            onClick={() => openTwilioAlert(r)}
            className="rounded-md bg-emerald-600 px-3 py-1 text-xs font-semibold text-white hover:bg-emerald-500 flex items-center gap-1"
          >
            <Phone className="h-3 w-3" />
            <span>SMS Alert</span>
          </button>
          <button
            onClick={() => goToSimulate(r.areaId)}
            className="rounded-md bg-navy-900 px-3 py-1 text-xs font-semibold text-white hover:bg-navy-800"
          >
            Simulate
          </button>
        </div>
      ),
    },
  ];

  const stateOptions = ["All States", ...Object.keys(STATE_COUNTY_MAP)];
  const specialtyOptions = ["All Specialties", ...(filterOptions?.specialties ?? [])];
  const riskOptions = ["All", "Low", "Medium", "High", "Critical"];

  return (
    <DashboardLayout title="Recommendations" subtitle="Where to recruit providers next">
      <PageHeader
        eyebrow="Recruitment Strategy"
        title="Provider Recruitment Recommendations"
        description="Prioritized list of counties and specialties where adding providers will have the greatest expected impact on access."
      />

      {loading || !summary ? (
        <LoadingState label="Loading recommendations..." />
      ) : (
        <div className="space-y-6">
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
            <KpiCard
              icon={Target}
              label="Critical Recruitment Areas"
              value={String(summary.criticalRecruitmentAreas)}
              helperText="Requiring immediate action"
              accent="risk"
            />
            <KpiCard
              icon={Users2}
              label="Total Providers Recommended"
              value={String(summary.totalProvidersRecommended)}
              helperText="Across all flagged areas"
            />
            <KpiCard
              icon={TrendingUp}
              label="Highest Risk"
              value={`${summary.highestRiskPct}%`}
              helperText="Top-priority area"
              accent="risk"
            />
            <KpiCard
              icon={Lightbulb}
              label="Potential Access Improvement"
              value={`${summary.potentialAccessImprovementPct}%`}
              helperText="If recommendations are applied"
            />
          </div>

          <FilterPanel
            fields={[
              { key: "state", label: "State", options: stateOptions },
              { key: "specialty", label: "Specialty", options: specialtyOptions },
              { key: "riskLevel", label: "Risk Level", options: riskOptions },
            ]}
            values={filters as unknown as Record<string, string>}
            onChange={(key, value) => setFilters((prev) => ({ ...prev, [key]: value }))}
            onReset={() => setFilters({ state: "All States", specialty: "All Specialties", riskLevel: "All" })}
            resultCount={searchedRows.length}
          />

          <ChartCard
            title="Recruitment Priority Table"
            subtitle="Sorted by Expected Impact by default — click a column to re-sort"
            action={
              <div className="relative flex items-center">
                <Search className="absolute left-3 h-3.5 w-3.5 text-slate-400" />
                <input
                  type="text"
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  placeholder="Search priority areas, specialties, diseases..."
                  className="h-8 w-60 sm:w-80 rounded-lg border border-surface-border bg-white pl-8 pr-7 text-xs text-navy-900 placeholder:text-slate-400 focus:border-brand-500 focus:outline-none focus:ring-1 focus:ring-brand-500"
                />
                {searchQuery && (
                  <button
                    onClick={() => setSearchQuery("")}
                    className="absolute right-2 text-slate-400 hover:text-slate-600"
                  >
                    <X className="h-3.5 w-3.5" />
                  </button>
                )}
              </div>
            }
          >
            <DataTable columns={columns} rows={searchedRows} getRowKey={(r) => `${r.areaId}-${r.specialty}`} />
          </ChartCard>
        </div>
      )}

      <TwilioAlertModal
        isOpen={twilioModalOpen}
        onClose={() => setTwilioModalOpen(false)}
        defaultCountyName={selectedRec?.areaName}
        defaultSpecialty={selectedRec?.specialty}
        defaultGapLevel={`${selectedRec?.riskScore}% Risk`}
      />
    </DashboardLayout>
  );
}

function cap(s: string): string {
  return s.charAt(0).toUpperCase() + s.slice(1);
}
