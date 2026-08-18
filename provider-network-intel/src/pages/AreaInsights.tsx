import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import {
  Users,
  Stethoscope,
  Activity,
  MapPinned,
  Route,
  Gauge,
  AlertCircle,
} from "lucide-react";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip,
  Legend,
} from "recharts";
import DashboardLayout from "../components/DashboardLayout";
import PageHeader from "../components/PageHeader";
import ChartCard from "../components/ChartCard";
import RiskBadge from "../components/RiskBadge";
import RecommendationCard from "../components/RecommendationCard";
import LoadingState from "../components/LoadingState";
import EmptyState from "../components/EmptyState";
import { useSelectedArea } from "../context/SelectedAreaContext";
import { getAreaDetails } from "../services/api";
import type { Area } from "../types";

const FACTOR_LABELS: { key: keyof Area["riskFactors"]; label: string }[] = [
  { key: "demandPressure", label: "Demand Pressure" },
  { key: "providerShortage", label: "Provider Shortage" },
  { key: "travelDistance", label: "Distance" },
  { key: "utilization", label: "Utilization" },
];

export default function AreaInsights() {
  const navigate = useNavigate();
  const { selectedAreaId } = useSelectedArea();
  const [loading, setLoading] = useState(true);
  const [area, setArea] = useState<Area | null>(null);

  useEffect(() => {
    if (!selectedAreaId) {
      setLoading(false);
      return;
    }
    setLoading(true);
    getAreaDetails(selectedAreaId).then((a) => {
      setArea(a);
      setLoading(false);
    });
  }, [selectedAreaId]);

  const supplyDemandData = area
    ? [
        { name: "Current Supply", value: area.providerSupply },
        { name: "Recommended Supply", value: area.providerSupply + area.providersNeeded },
      ]
    : [];

  const travelBuckets = area
    ? [
        { range: "0-10 km", patients: Math.round(area.population * 0.00012) },
        { range: "10-20 km", patients: Math.round(area.population * 0.0002) },
        { range: "20-30 km", patients: Math.round(area.population * 0.00026) },
        { range: "30-40 km", patients: Math.round(area.population * (area.avgTravelDistanceKm > 25 ? 0.00034 : 0.00014)) },
        { range: "40+ km", patients: Math.round(area.population * (area.avgTravelDistanceKm > 30 ? 0.0002 : 0.00006)) },
      ]
    : [];

  return (
    <DashboardLayout title="Area Insights" subtitle="Detailed access analysis for a selected area">
      {loading ? (
        <LoadingState label="Loading area insights..." />
      ) : !area ? (
        <EmptyState
          icon={AlertCircle}
          title="No area selected"
          description="Choose an area from the Dashboard, Explore Network, or Recommendations to see its detailed access analysis here."
          action={
            <button
              onClick={() => navigate("/map")}
              className="rounded-lg bg-brand-600 px-4 py-2 text-sm font-semibold text-white hover:bg-brand-700"
            >
              Open Explore Network
            </button>
          }
        />
      ) : (
        <div className="space-y-6">
          <PageHeader
            eyebrow="Network Access Analysis"
            title={`${area.name}, ${area.state}`}
            description={`Last updated ${area.lastUpdated}`}
            actions={
              <div className="flex flex-wrap items-center gap-2">
                <RiskBadge level={area.riskLevel} score={area.riskScore} size="lg" />
              </div>
            }
          />

          {/* KPI cards */}
          <div className="grid grid-cols-2 gap-4 sm:grid-cols-3 lg:grid-cols-6">
            <MiniKpi icon={Users} label="Population" value={area.population.toLocaleString()} />
            <MiniKpi icon={Stethoscope} label="Provider Supply" value={String(area.providerSupply)} />
            <MiniKpi icon={Activity} label="Disease Demand" value={cap(area.demandLevel)} />
            <MiniKpi icon={MapPinned} label="Access Gap" value={cap(area.accessGap)} />
            <MiniKpi icon={Route} label="Avg. Travel Distance" value={`${area.avgTravelDistanceKm} km`} />
            <MiniKpi icon={Gauge} label="Network Adequacy" value={`${area.networkAdequacyPct}%`} />
          </div>

          {/* Root cause */}
          <ChartCard title="Why is this area at risk?" subtitle="Root cause analysis (prototype logic)">
            <p className="mb-4 text-sm leading-relaxed text-slate-600">
              High population demand combined with insufficient {area.primarySpecialty.toLowerCase()} provider
              supply and a {area.avgTravelDistanceKm} km average travel distance is creating a
              {" "}
              <span className="font-semibold text-navy-900">{area.accessGap}</span> provider access gap in this
              area.
            </p>
            <div className="grid grid-cols-1 gap-3 sm:grid-cols-2 lg:grid-cols-4">
              {FACTOR_LABELS.map((f) => (
                <div key={f.key} className="rounded-xl border border-surface-border p-3">
                  <p className="text-xs font-medium text-slate-500">{f.label}</p>
                  <div className="mt-2 h-2 w-full overflow-hidden rounded-full bg-surface">
                    <div
                      className="h-full rounded-full bg-brand-500"
                      style={{ width: `${area.riskFactors[f.key]}%` }}
                    />
                  </div>
                  <p className="mt-1 text-right text-xs font-semibold text-navy-900">{area.riskFactors[f.key]}%</p>
                </div>
              ))}
            </div>
          </ChartCard>

          {/* Recommendation */}
          <RecommendationCard
            specialty={area.primarySpecialty}
            providersRequired={area.providersNeeded}
            confidencePct={area.recommendationConfidencePct}
            expectedImpact={area.expectedImpact}
            actions={
              <>
                <button
                  onClick={() => navigate("/recommendations")}
                  className="rounded-lg bg-brand-600 px-4 py-2 text-xs font-semibold text-white hover:bg-brand-700"
                >
                  View Recommendation
                </button>
                <button
                  onClick={() => navigate("/what-if")}
                  className="rounded-lg border border-brand-300 bg-white px-4 py-2 text-xs font-semibold text-brand-700 hover:bg-brand-50"
                >
                  Run What-if Analysis
                </button>
              </>
            }
          />

          {/* Charts */}
          <div className="grid grid-cols-1 gap-4 lg:grid-cols-2">
            <ChartCard title="Provider Supply vs. Demand" subtitle="Current vs. recommended provider count">
              <ResponsiveContainer width="100%" height={220}>
                <BarChart data={supplyDemandData}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#e4e9f2" vertical={false} />
                  <XAxis dataKey="name" tick={{ fontSize: 11, fill: "#94a3b8" }} axisLine={false} tickLine={false} />
                  <YAxis tick={{ fontSize: 11, fill: "#94a3b8" }} axisLine={false} tickLine={false} />
                  <Tooltip contentStyle={{ borderRadius: 10, border: "1px solid #e4e9f2", fontSize: 12 }} />
                  <Bar dataKey="value" fill="#2f6ce8" radius={[6, 6, 0, 0]} barSize={56} />
                </BarChart>
              </ResponsiveContainer>
            </ChartCard>

            <ChartCard title="Travel Distance Distribution" subtitle="Estimated patients by distance band">
              <ResponsiveContainer width="100%" height={220}>
                <BarChart data={travelBuckets}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#e4e9f2" vertical={false} />
                  <XAxis dataKey="range" tick={{ fontSize: 10, fill: "#94a3b8" }} axisLine={false} tickLine={false} />
                  <YAxis tick={{ fontSize: 11, fill: "#94a3b8" }} axisLine={false} tickLine={false} />
                  <Tooltip contentStyle={{ borderRadius: 10, border: "1px solid #e4e9f2", fontSize: 12 }} />
                  <Bar dataKey="patients" fill="#f59e0b" radius={[6, 6, 0, 0]} barSize={32} />
                </BarChart>
              </ResponsiveContainer>
            </ChartCard>
          </div>

          <ChartCard title="Risk Factors" subtitle="Relative contribution to overall risk score">
            <ResponsiveContainer width="100%" height={220}>
              <BarChart
                data={FACTOR_LABELS.map((f) => ({ label: f.label, value: area.riskFactors[f.key] }))}
                layout="vertical"
                margin={{ left: 8, right: 24 }}
              >
                <CartesianGrid strokeDasharray="3 3" horizontal={false} stroke="#e4e9f2" />
                <XAxis type="number" domain={[0, 100]} tick={{ fontSize: 11, fill: "#94a3b8" }} axisLine={false} tickLine={false} />
                <YAxis type="category" dataKey="label" width={130} tick={{ fontSize: 11, fill: "#334155" }} axisLine={false} tickLine={false} />
                <Tooltip contentStyle={{ borderRadius: 10, border: "1px solid #e4e9f2", fontSize: 12 }} />
                <Legend wrapperStyle={{ fontSize: 11 }} />
                <Bar dataKey="value" name="Score" fill="#dc2626" radius={[0, 6, 6, 0]} barSize={18} />
              </BarChart>
            </ResponsiveContainer>
          </ChartCard>
        </div>
      )}
    </DashboardLayout>
  );
}

function MiniKpi({ icon: Icon, label, value }: { icon: typeof Users; label: string; value: string }) {
  return (
    <div className="rounded-xl border border-surface-border bg-surface-card p-4 shadow-card">
      <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-brand-100 text-brand-700">
        <Icon className="h-4 w-4" />
      </div>
      <p className="mt-2 text-xs font-medium text-slate-500">{label}</p>
      <p className="mt-0.5 text-lg font-bold text-navy-900">{value}</p>
    </div>
  );
}

function cap(s: string): string {
  return s.charAt(0).toUpperCase() + s.slice(1);
}
