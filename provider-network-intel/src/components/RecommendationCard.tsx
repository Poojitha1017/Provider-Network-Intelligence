import { Sparkles } from "lucide-react";
import type { ImpactLevel, Specialty } from "../types";
import StatusBadge from "./StatusBadge";

interface RecommendationCardProps {
  specialty: Specialty;
  providersRequired: number;
  confidencePct: number;
  expectedImpact: ImpactLevel;
  actions?: React.ReactNode;
}

const IMPACT_TONE: Record<ImpactLevel, "positive" | "warning" | "negative"> = {
  low: "warning",
  medium: "warning",
  high: "positive",
};

export default function RecommendationCard({
  specialty,
  providersRequired,
  confidencePct,
  expectedImpact,
  actions,
}: RecommendationCardProps) {
  return (
    <div className="rounded-2xl border border-brand-100 bg-brand-50/60 p-5">
      <div className="mb-3 flex items-center gap-2">
        <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-brand-600 text-white">
          <Sparkles className="h-4 w-4" />
        </div>
        <p className="text-sm font-semibold text-brand-800">Recommended Action</p>
      </div>
      <div className="grid grid-cols-2 gap-4 sm:grid-cols-4">
        <div>
          <p className="text-xs font-medium text-slate-500">Recommended Specialty</p>
          <p className="mt-1 text-lg font-bold text-navy-900">{specialty}</p>
        </div>
        <div>
          <p className="text-xs font-medium text-slate-500">Providers Required</p>
          <p className="mt-1 text-lg font-bold text-navy-900">{providersRequired}</p>
        </div>
        <div>
          <p className="text-xs font-medium text-slate-500">Confidence</p>
          <p className="mt-1 text-lg font-bold text-navy-900">{confidencePct}%</p>
        </div>
        <div>
          <p className="text-xs font-medium text-slate-500">Expected Impact</p>
          <div className="mt-1">
            <StatusBadge label={expectedImpact[0].toUpperCase() + expectedImpact.slice(1)} tone={IMPACT_TONE[expectedImpact]} />
          </div>
        </div>
      </div>
      {actions && <div className="mt-4 flex flex-wrap gap-2">{actions}</div>}
    </div>
  );
}
