import { useEffect, useMemo, useState } from "react";
import { useNavigate } from "react-router-dom";
import {
  Building2,
  Users,
  AlertTriangle,
  MapPinned,
  Route,
  Search,
  X,
} from "lucide-react";
import {
  PieChart,
  Pie,
  Cell,
  ResponsiveContainer,
  Tooltip,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  LineChart,
  Line,
  Legend,
} from "recharts";
import DashboardLayout from "../components/DashboardLayout";
import PageHeader from "../components/PageHeader";
import KpiCard from "../components/KpiCard";
import ChartCard from "../components/ChartCard";
import DataTable, { type DataTableColumn } from "../components/DataTable";
import RiskBadge, { riskHex } from "../components/RiskBadge";
import LoadingState from "../components/LoadingState";
import { getDashboardData } from "../services/api";
import { useSelectedArea } from "../context/SelectedAreaContext";
import type { Area, DashboardMetrics, RiskDistributionSlice, SpecialtyGapDatum, TrendPoint } from "../types";

export default function Dashboard() {
  const navigate = useNavigate();
  const { setSelectedAreaId } = useSelectedArea();

  const [loading, setLoading] = useState(true);
  const [metrics, setMetrics] = useState<DashboardMetrics | null>(null);
  const [riskDistribution, setRiskDistribution] = useState<RiskDistributionSlice[]>([]);
  const [specialtyGaps, setSpecialtyGaps] = useState<SpecialtyGapDatum[]>([]);
  const [trend, setTrend] = useState<TrendPoint[]>([]);
  const [topAreas, setTopAreas] = useState<Area[]>([]);

  useEffect(() => {
    let active = true;
    getDashboardData().then((data) => {
      if (!active) return;
      setMetrics(data.metrics);
      setRiskDistribution(data.riskDistribution);
      setSpecialtyGaps(data.specialtyGaps);
      setTrend(data.trend);
      setTopAreas(data.topCriticalAreas);
      setLoading(false);
    });
    return () => {
      active = false;
    };
  }, []);

  function viewArea(area: Area) {
    setSelectedAreaId(area.id);
    navigate("/area-insights");
  }

  const columns: DataTableColumn<Area>[] = [
    { key: "rank", header: "Rank", render: (a) => `#${topAreas.indexOf(a) + 1}`, widthClass: "w-14" },
    { key: "area", header: "Area", render: (a) => <span className="font-semibold">{a.name}</span> },
    { key: "state", header: "State", render: (a) => a.state },
    { key: "specialty", header: "Specialty", render: (a) => a.primarySpecialty },
    { key: "risk", header: "Risk Score", render: (a) => <span className="font-semibold">{a.riskScore}%</span> },
    { key: "needed", header: "Providers Needed", render: (a) => a.providersNeeded },
    { key: "status", header: "Status", render: (a) => <RiskBadge level={a.riskLevel} size="sm" /> },
    {
      key: "action",
      header: "Action",
      align: "right",
      render: (a) => (
        <button
          onClick={() => viewArea(a)}
          className="rounded-md border border-brand-200 px-3 py-1 text-xs font-semibold text-brand-700 hover:bg-brand-50"
        >
          View
        </button>
      ),
    },
  ];

  const [searchQuery, setSearchQuery] = useState("");

  const filteredTopAreas = useMemo(() => {
    if (!searchQuery.trim()) return topAreas;
    const q = searchQuery.toLowerCase().trim();
    return topAreas.filter(
      (a) =>
        a.name.toLowerCase().includes(q) ||
        a.state.toLowerCase().includes(q) ||
        a.primarySpecialty.toLowerCase().includes(q) ||
        a.riskLevel.toLowerCase().includes(q) ||
        (a.county_fips && a.county_fips.includes(q))
    );
  }, [topAreas, searchQuery]);

  return (
    <DashboardLayout>
      <PageHeader
        title="Network Health at a Glance"
        description="Monitor access gaps, high-risk areas, and provider supply across your entire network"
      />

      {loading || !metrics ? (
        <LoadingState label="Loading network overview..." />
      ) : (
        <div className="space-y-6">
          {/* KPI cards */}
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-5">
            <KpiCard
              icon={Building2}
              label="Total Areas"
              value={metrics.totalAreas.toLocaleString()}
              helperText="Monitored service areas"
              trendPct={metrics.totalAreasTrendPct}
            />
            <KpiCard
              icon={Users}
              label="Total Providers"
              value={metrics.totalProviders.toLocaleString()}
              helperText="Active in-network providers"
              trendPct={metrics.totalProvidersTrendPct}
            />
            <KpiCard
              icon={AlertTriangle}
              label="High Risk Areas"
              value={metrics.highRiskAreas.toLocaleString()}
              helperText="Risk score ≥ 65%"
              trendPct={metrics.highRiskAreasTrendPct}
              trendGoodDirection="down"
              accent="risk"
            />
            <KpiCard
              icon={MapPinned}
              label="Access Gap Areas"
              value={metrics.accessGapAreas.toLocaleString()}
              helperText="Below adequacy threshold"
              trendPct={metrics.accessGapAreasTrendPct}
              trendGoodDirection="down"
            />
            <KpiCard
              icon={Route}
              label="Avg. Travel Distance"
              value={`${metrics.avgTravelDistanceKm} km`}
              helperText="To nearest specialist"
              trendPct={metrics.avgTravelDistanceTrendPct}
              trendGoodDirection="down"
            />
          </div>

          {/* Charts */}
          <div className="grid grid-cols-1 gap-4 lg:grid-cols-3">
            <ChartCard title="Access Gap by Risk Level" subtitle="Share of areas per risk tier">
              <div className="flex items-center gap-4">
                <ResponsiveContainer width="100%" height={200}>
                  <PieChart>
                    <Pie
                      data={riskDistribution}
                      dataKey="areaCount"
                      nameKey="label"
                      innerRadius={55}
                      outerRadius={80}
                      paddingAngle={2}
                    >
                      {riskDistribution.map((slice) => (
                        <Cell key={slice.level} fill={riskHex(slice.level)} />
                      ))}
                    </Pie>
                    <Tooltip
                      formatter={(value, _name, item) => [`${Number(value)} areas`, item.payload.label]}
                      contentStyle={{ borderRadius: 10, border: "1px solid #e4e9f2", fontSize: 12 }}
                    />
                  </PieChart>
                </ResponsiveContainer>
              </div>
              <ul className="mt-1 space-y-1.5">
                {riskDistribution.map((slice) => (
                  <li key={slice.level} className="flex items-center justify-between text-xs">
                    <span className="flex items-center gap-1.5 text-slate-500">
                      <span className="h-2 w-2 rounded-full" style={{ backgroundColor: riskHex(slice.level) }} />
                      {slice.label}
                    </span>
                    <span className="font-semibold text-navy-900">{slice.areaCount}</span>
                  </li>
                ))}
              </ul>
            </ChartCard>

            <ChartCard title="Access Gap by Specialty" subtitle="Areas with unmet demand">
              <ResponsiveContainer width="100%" height={260}>
                <BarChart data={specialtyGaps} layout="vertical" margin={{ left: 8, right: 16 }}>
                  <CartesianGrid strokeDasharray="3 3" horizontal={false} stroke="#e4e9f2" />
                  <XAxis type="number" tick={{ fontSize: 11, fill: "#94a3b8" }} axisLine={false} tickLine={false} />
                  <YAxis
                    type="category"
                    dataKey="specialty"
                    width={92}
                    tick={{ fontSize: 11, fill: "#334155" }}
                    axisLine={false}
                    tickLine={false}
                  />
                  <Tooltip
                    formatter={(v) => [`${Number(v)} areas`, "Access gap"]}
                    contentStyle={{ borderRadius: 10, border: "1px solid #e4e9f2", fontSize: 12 }}
                  />
                  <Bar dataKey="areasWithGap" fill="#2f6ce8" radius={[0, 6, 6, 0]} barSize={16} />
                </BarChart>
              </ResponsiveContainer>
            </ChartCard>

            <ChartCard title="Access Gap Trend" subtitle="Monthly, network-wide">
              <ResponsiveContainer width="100%" height={260}>
                <LineChart data={trend} margin={{ left: -16, right: 8 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#e4e9f2" />
                  <XAxis dataKey="month" tick={{ fontSize: 11, fill: "#94a3b8" }} axisLine={false} tickLine={false} />
                  <YAxis tick={{ fontSize: 11, fill: "#94a3b8" }} axisLine={false} tickLine={false} />
                  <Tooltip contentStyle={{ borderRadius: 10, border: "1px solid #e4e9f2", fontSize: 12 }} />
                  <Legend wrapperStyle={{ fontSize: 11 }} />
                  <Line
                    type="monotone"
                    dataKey="accessGapAreas"
                    name="Access gap areas"
                    stroke="#2f6ce8"
                    strokeWidth={2.5}
                    dot={{ r: 3 }}
                  />
                </LineChart>
              </ResponsiveContainer>
            </ChartCard>
          </div>

          {/* Top critical areas */}
          <ChartCard
            title="Top Critical Areas"
            subtitle="Highest network risk right now"
            action={
              <div className="relative flex items-center">
                <Search className="absolute left-3 h-3.5 w-3.5 text-slate-400" />
                <input
                  type="text"
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  placeholder="Search critical areas, specialties, states..."
                  className="h-8 w-60 sm:w-72 rounded-lg border border-surface-border bg-white pl-8 pr-7 text-xs text-navy-900 placeholder:text-slate-400 focus:border-brand-500 focus:outline-none focus:ring-1 focus:ring-brand-500"
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
            <DataTable columns={columns} rows={filteredTopAreas} getRowKey={(a) => a.id} />
          </ChartCard>
        </div>
      )}
    </DashboardLayout>
  );
}
