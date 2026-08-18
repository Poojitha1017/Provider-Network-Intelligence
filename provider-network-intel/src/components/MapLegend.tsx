const ITEMS: { level: string; color: string; label: string }[] = [
  { level: "low", color: "#16a34a", label: "Low Risk" },
  { level: "medium", color: "#d97706", label: "Medium Risk" },
  { level: "high", color: "#ea580c", label: "High Risk" },
  { level: "critical", color: "#dc2626", label: "Critical Risk" },
];

export default function MapLegend() {
  return (
    <div className="rounded-xl border border-surface-border bg-white/95 px-4 py-3 shadow-popover backdrop-blur">
      <p className="mb-2 text-[11px] font-semibold uppercase tracking-wide text-slate-400">Risk Level</p>
      <ul className="space-y-1.5">
        {ITEMS.map((item) => (
          <li key={item.level} className="flex items-center gap-2 text-xs font-medium text-navy-900">
            <span className="h-2.5 w-2.5 rounded-full" style={{ backgroundColor: item.color }} />
            {item.label}
          </li>
        ))}
      </ul>
    </div>
  );
}
