import type { RiskLevel } from "../types";

const STYLES: Record<RiskLevel, { bg: string; text: string; dot: string; label: string }> = {
  low: { bg: "bg-risk-lowbg", text: "text-risk-low", dot: "bg-risk-low", label: "Low Risk" },
  medium: { bg: "bg-risk-mediumbg", text: "text-risk-medium", dot: "bg-risk-medium", label: "Medium Risk" },
  high: { bg: "bg-risk-highbg", text: "text-risk-high", dot: "bg-risk-high", label: "High Risk" },
  critical: { bg: "bg-risk-criticalbg", text: "text-risk-critical", dot: "bg-risk-critical", label: "Critical Risk" },
};

interface RiskBadgeProps {
  level: RiskLevel;
  score?: number;
  size?: "sm" | "md" | "lg";
  className?: string;
}

export default function RiskBadge({ level, score, size = "md", className = "" }: RiskBadgeProps) {
  const s = STYLES[level];
  const sizing =
    size === "lg"
      ? "px-4 py-1.5 text-sm gap-2"
      : size === "sm"
        ? "px-2 py-0.5 text-[11px] gap-1"
        : "px-2.5 py-1 text-xs gap-1.5";

  return (
    <span
      className={`inline-flex items-center rounded-full font-semibold ${s.bg} ${s.text} ${sizing} ${className}`}
    >
      <span className={`inline-block h-1.5 w-1.5 rounded-full ${s.dot}`} aria-hidden="true" />
      {s.label}
      {typeof score === "number" && <span className="opacity-80">· {score}%</span>}
    </span>
  );
}

export function riskDotColor(level: RiskLevel): string {
  return STYLES[level].dot;
}

export function riskHex(level: RiskLevel): string {
  switch (level) {
    case "low":
      return "#16a34a";
    case "medium":
      return "#d97706";
    case "high":
      return "#ea580c";
    case "critical":
      return "#dc2626";
  }
}
