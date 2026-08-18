import type { ReactNode } from "react";
import Topbar from "./Topbar";
import FloatingChat from "./FloatingChat";

interface DashboardLayoutProps {
  title?: string;
  subtitle?: string;
  children: ReactNode;
}

export default function DashboardLayout({ children }: DashboardLayoutProps) {
  return (
    <div className="relative flex h-screen flex-col overflow-hidden bg-surface">
      <Topbar />
      <main className="flex-1 overflow-y-auto px-6 py-6">{children}</main>
      <FloatingChat />
    </div>
  );
}
