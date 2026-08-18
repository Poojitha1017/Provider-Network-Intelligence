import type { ReactNode } from "react";
import logo from "../assets/logo.png";

interface AuthLayoutProps {
  title: string;
  children: ReactNode;
}

const PATTERN_SVG = encodeURIComponent(`
<svg xmlns="http://www.w3.org/2000/svg" width="220" height="220" viewBox="0 0 220 220">
  <g fill="none" stroke="#3a5a8f" stroke-width="1" opacity="0.35">
    <line x1="20" y1="30" x2="70" y2="70" />
    <line x1="70" y1="70" x2="140" y2="40" />
    <line x1="70" y1="70" x2="60" y2="150" />
    <line x1="140" y1="40" x2="190" y2="90" />
    <line x1="60" y1="150" x2="120" y2="190" />
    <line x1="60" y1="150" x2="10" y2="190" />
    <line x1="140" y1="40" x2="120" y2="190" />
  </g>
  <g fill="none" stroke="#3a5a8f" stroke-width="1.5" opacity="0.5">
    <circle cx="20" cy="30" r="5" />
    <circle cx="70" cy="70" r="6" />
    <circle cx="140" cy="40" r="5" />
    <circle cx="190" cy="90" r="4" />
    <circle cx="60" cy="150" r="6" />
    <circle cx="120" cy="190" r="5" />
    <circle cx="10" cy="190" r="4" />
  </g>
</svg>
`);

export default function AuthLayout({ title, children }: AuthLayoutProps) {
  return (
    <div className="relative flex min-h-screen w-full items-center justify-center overflow-hidden bg-navy-950 px-4 py-10">
      {/* Subtle network pattern background */}
      <div
        className="pointer-events-none absolute inset-0 opacity-60"
        style={{
          backgroundImage: `url("data:image/svg+xml,${PATTERN_SVG}")`,
          backgroundSize: "220px 220px",
        }}
      />
      <div className="pointer-events-none absolute inset-0 bg-gradient-to-b from-navy-950/40 via-navy-950/70 to-navy-950" />

      <div className="relative z-10 w-full max-w-md">
        {/* Logo + brand */}
        <div className="mb-6 text-center">
          <img
            src={logo}
            alt="Provider Intelligence Engine"
            className="mx-auto h-24 w-24 rounded-3xl object-cover shadow-2xl ring-1 ring-white/10"
          />
          <h1 className="mt-5 text-2xl font-extrabold leading-tight text-white sm:text-[28px]">
            Provider Intelligence{" "}
            <span className="bg-gradient-to-r from-brand-400 to-emerald-400 bg-clip-text text-transparent">
              Engine
            </span>
          </h1>
          <p className="mt-1.5 text-sm text-slate-400">Intelligent Insights for Better Provider Access</p>
        </div>

        {/* Card */}
        <div className="rounded-3xl border border-white/10 bg-navy-900/90 p-7 shadow-2xl backdrop-blur sm:p-8">
          <p className="mb-6 text-center text-[15px] font-medium text-slate-300">{title}</p>
          {children}
        </div>
      </div>
    </div>
  );
}
