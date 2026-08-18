import { RotateCcw } from "lucide-react";

interface SelectField {
  key: string;
  label: string;
  options: string[];
}

interface FilterPanelProps {
  fields: SelectField[];
  values: Record<string, string>;
  onChange: (key: string, value: string) => void;
  onReset: () => void;
  resultCount?: number;
}

export default function FilterPanel({ fields, values, onChange, onReset, resultCount }: FilterPanelProps) {
  return (
    <div className="rounded-2xl border border-surface-border bg-surface-card p-4 shadow-card">
      <div className="flex flex-wrap items-end gap-3">
        {fields.map((field) => (
          <label key={field.key} className="flex min-w-[150px] flex-1 flex-col gap-1">
            <span className="text-xs font-semibold text-slate-500">{field.label}</span>
            <select
              value={values[field.key]}
              onChange={(e) => onChange(field.key, e.target.value)}
              className="rounded-lg border border-surface-border bg-white px-3 py-2 text-sm text-navy-900 focus:border-brand-500 focus:outline-none focus:ring-2 focus:ring-brand-100"
            >
              {field.options.map((opt) => (
                <option key={opt} value={opt}>
                  {opt}
                </option>
              ))}
            </select>
          </label>
        ))}
        <button
          type="button"
          onClick={onReset}
          className="flex items-center gap-1.5 rounded-lg border border-surface-border px-3 py-2 text-sm font-medium text-slate-600 hover:bg-surface"
        >
          <RotateCcw className="h-3.5 w-3.5" />
          Reset
        </button>
      </div>
      {typeof resultCount === "number" && (
        <p className="mt-3 text-xs font-medium text-slate-400">
          Showing <span className="text-navy-900">{resultCount}</span> matching area{resultCount === 1 ? "" : "s"}
        </p>
      )}
    </div>
  );
}
