import { NavLink, useNavigate } from "react-router-dom";
import {
  Home,
  Map,
  Building2,
  Lightbulb,
  SlidersHorizontal,
  Bell,
  LogOut,
  ChevronDown,
} from "lucide-react";
import { useState } from "react";
import { useAuth } from "../context/AuthContext";
import logo from "../assets/logo.png";

const NAV_ITEMS = [
  { to: "/dashboard", label: "Home", icon: Home },
  { to: "/map", label: "Explore Network", icon: Map },
  { to: "/area-insights", label: "Area Insights", icon: Building2 },
  { to: "/recommendations", label: "Recommendations", icon: Lightbulb },
  { to: "/what-if", label: "What-if Simulator", icon: SlidersHorizontal },
];

export default function Topbar() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const [showMenu, setShowMenu] = useState(false);
  const [showNotifications, setShowNotifications] = useState(false);

  const handleLogout = () => {
    logout();
    navigate("/login", { replace: true });
  };

  return (
    <header className="flex h-16 shrink-0 items-center gap-3 border-b border-navy-800 bg-navy-900 px-4 lg:px-6">
      <div className="flex shrink-0 items-center gap-2.5 pr-4">
        <img src={logo} alt="Provider Intelligence Engine" className="h-9 w-9 shrink-0 rounded-lg object-cover" />
        <div className="hidden min-w-0 sm:block">
          <p className="truncate text-sm font-bold leading-tight text-white">Provider Intelligence Engine</p>
          <p className="truncate text-[11px] leading-tight text-slate-400">
            Intelligent Insights for Better Provider Access
          </p>
        </div>
      </div>

      <nav
        className="flex flex-1 items-center gap-1 overflow-x-auto"
        aria-label="Main navigation"
      >
        {NAV_ITEMS.map((item) => (
          <NavLink
            key={item.to}
            to={item.to}
            className={({ isActive }) =>
              `flex shrink-0 items-center gap-2 rounded-lg px-3 py-2 text-sm font-medium transition-colors ${
                isActive
                  ? "bg-brand-600 text-white shadow-sm"
                  : "text-slate-300 hover:bg-navy-800 hover:text-white"
              }`
            }
          >
            <item.icon className="h-[18px] w-[18px] shrink-0" strokeWidth={2} />
            <span className="whitespace-nowrap">{item.label}</span>
          </NavLink>
        ))}
      </nav>

      <div className="relative shrink-0">
        <button
          type="button"
          onClick={() => setShowNotifications((s) => !s)}
          aria-label="Notifications"
          className="relative flex h-9 w-9 items-center justify-center rounded-lg border border-navy-800 text-slate-300 hover:bg-navy-800 hover:text-white"
        >
          <Bell className="h-4 w-4" />
          <span className="absolute right-1.5 top-1.5 h-1.5 w-1.5 rounded-full bg-risk-critical" />
        </button>
        {showNotifications && (
          <div className="absolute right-0 top-11 z-30 w-72 rounded-xl border border-surface-border bg-white p-3 shadow-popover">
            <p className="mb-2 text-xs font-semibold uppercase tracking-wide text-slate-400">Notifications</p>
            <div className="space-y-2 text-sm">
              <div className="rounded-lg bg-surface p-2.5">
                <p className="font-medium text-navy-900">Dallas North flagged critical</p>
                <p className="text-xs text-slate-400">Risk score rose to 91%</p>
              </div>
              <div className="rounded-lg bg-surface p-2.5">
                <p className="font-medium text-navy-900">New recommendation available</p>
                <p className="text-xs text-slate-400">Atlanta Southside · Oncology</p>
              </div>
            </div>
          </div>
        )}
      </div>

      <div className="relative shrink-0">
        <button
          type="button"
          onClick={() => setShowMenu((s) => !s)}
          className="flex items-center gap-2 rounded-lg border border-navy-800 py-1.5 pl-1.5 pr-2.5 hover:bg-navy-800"
        >
          <div className="flex h-7 w-7 items-center justify-center rounded-full bg-brand-600 text-xs font-bold text-white">
            {(user?.fullName ?? "?")
              .split(" ")
              .map((p) => p[0])
              .join("")
              .slice(0, 2)
              .toUpperCase()}
          </div>
          <div className="hidden text-left sm:block">
            <p className="text-xs font-semibold leading-tight text-white">{user?.fullName}</p>
            <p className="text-[11px] leading-tight text-slate-400">{user?.role}</p>
          </div>
          <ChevronDown className="h-3.5 w-3.5 text-slate-400" />
        </button>

        {showMenu && (
          <div className="absolute right-0 top-11 z-30 w-56 rounded-xl border border-surface-border bg-white p-1.5 shadow-popover">
            <div className="border-b border-surface-border px-2.5 py-2">
              <p className="truncate text-sm font-semibold text-navy-900">{user?.fullName}</p>
              <p className="truncate text-xs text-slate-400">{user?.email}</p>
            </div>
            <button
              type="button"
              onClick={handleLogout}
              className="mt-1 flex w-full items-center gap-2 rounded-lg px-2.5 py-2 text-sm font-medium text-risk-critical hover:bg-risk-criticalbg"
            >
              <LogOut className="h-4 w-4" />
              Sign out
            </button>
          </div>
        )}
      </div>
    </header>
  );
}
