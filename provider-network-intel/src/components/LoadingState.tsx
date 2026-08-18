import { Loader2 } from "lucide-react";

interface LoadingStateProps {
  label?: string;
  className?: string;
}

export default function LoadingState({ label = "Loading...", className = "" }: LoadingStateProps) {
  return (
    <div className={`flex flex-col items-center justify-center gap-3 py-16 text-center ${className}`}>
      <Loader2 className="h-6 w-6 animate-spin text-brand-500" />
      <p className="text-sm font-medium text-slate-400">{label}</p>
    </div>
  );
}
