type Tone = "neutral" | "positive" | "warning" | "negative" | "info";

const TONE_STYLES: Record<Tone, string> = {
  neutral: "bg-slate-100 text-slate-700",
  positive: "bg-risk-lowbg text-risk-low",
  warning: "bg-risk-mediumbg text-risk-medium",
  negative: "bg-risk-criticalbg text-risk-critical",
  info: "bg-brand-100 text-brand-700",
};

interface StatusBadgeProps {
  label: string;
  tone?: Tone;
  className?: string;
}

export default function StatusBadge({ label, tone = "neutral", className = "" }: StatusBadgeProps) {
  return (
    <span
      className={`inline-flex items-center rounded-md px-2.5 py-1 text-xs font-semibold ${TONE_STYLES[tone]} ${className}`}
    >
      {label}
    </span>
  );
}
