import { createContext, useContext, useMemo, useState, type ReactNode } from "react";

interface SelectedAreaContextValue {
  selectedAreaId: string | null;
  setSelectedAreaId: (id: string | null) => void;
}

const SelectedAreaContext = createContext<SelectedAreaContextValue | undefined>(undefined);

export function SelectedAreaProvider({ children }: { children: ReactNode }) {
  const [selectedAreaId, setSelectedAreaId] = useState<string | null>("area-1");

  const value = useMemo(() => ({ selectedAreaId, setSelectedAreaId }), [selectedAreaId]);

  return <SelectedAreaContext.Provider value={value}>{children}</SelectedAreaContext.Provider>;
}

export function useSelectedArea(): SelectedAreaContextValue {
  const ctx = useContext(SelectedAreaContext);
  if (!ctx) throw new Error("useSelectedArea must be used within SelectedAreaProvider");
  return ctx;
}
