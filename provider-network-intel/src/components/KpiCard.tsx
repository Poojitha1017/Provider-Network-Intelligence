import type { LucideIcon } from "lucide-react";
import { ArrowDownRight, ArrowUpRight } from "lucide-react";

interface KpiCardProps {
  icon: LucideIcon;
  label: string;
  value: string;
  helperText?: string;
  trendPct?: number;
  trendGoodDirection?: "up" | "down";
  accent?: "brand" | "risk" | "navy";
}

export default function KpiCard({
  icon: Icon,
  label,
  value,
  helperText,
  trendPct,
  trendGoodDirection = "up",
  accent = "brand",
}: KpiCardProps) {
  const isUp = (trendPct ?? 0) >= 0;
  const isGood = trendGoodDirection === "up" ? isUp : !isUp;

  const iconBg =
    accent === "risk" ? "bg-risk-criticalbg text-risk-critical" : accent === "navy" ? "bg-navy-900 text-white" : "bg-brand-100 text-brand-700";

  return (
    <div className="rounded-2xl border border-surface-border bg-surface-card p-5 shadow-card">
      <div className="flex items-start justify-between">
        <div className={`flex h-10 w-10 items-center justify-center rounded-xl ${iconBg}`}>
          <Icon className="h-5 w-5" strokeWidth={2} />
        </div>
        {typeof trendPct === "number" && (
          <span
            className={`inline-flex items-center gap-0.5 rounded-full px-2 py-0.5 text-xs font-semibold ${
              isGood ? "bg-risk-lowbg text-risk-low" : "bg-risk-criticalbg text-risk-critical"
            }`}
          >
            {isUp ? <ArrowUpRight className="h-3 w-3" /> : <ArrowDownRight className="h-3 w-3" />}
            {Math.abs(trendPct)}%
          </span>
        )}
      </div>
      <p className="mt-4 text-sm font-medium text-slate-500">{label}</p>
      <p className="mt-1 text-2xl font-bold tracking-tight text-navy-900">{value}</p>
      {helperText && <p className="mt-1 text-xs text-slate-400">{helperText}</p>}
    </div>
  );
}
