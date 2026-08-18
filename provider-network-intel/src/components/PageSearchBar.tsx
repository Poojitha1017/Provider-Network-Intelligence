import { Search } from "lucide-react";

interface PageSearchBarProps {
  placeholder?: string;
}

export default function PageSearchBar({ placeholder = "Search areas, providers..." }: PageSearchBarProps) {
  return (
    <div className="flex items-center gap-2 rounded-lg border border-surface-border bg-surface-card px-3 py-2 text-sm text-slate-400 shadow-sm">
      <Search className="h-4 w-4 shrink-0" />
      <input
        type="text"
        placeholder={placeholder}
        className="w-44 bg-transparent text-sm text-navy-900 placeholder:text-slate-400 focus:outline-none sm:w-56"
      />
    </div>
  );
}
