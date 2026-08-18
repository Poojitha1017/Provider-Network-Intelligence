# Provider Network Intelligence

**Network Adequacy & Access Intelligence** — a frontend prototype for a
healthcare insurance payer / network manager to identify provider access
gaps, understand why they exist, and simulate provider recruitment.

This is a **frontend-only prototype**. Data comes from `src/data/mockData.ts`.
There is no backend, database, ML model, or login — the app opens straight
to the Dashboard. See "Connecting a real backend" below for how this is
designed to plug one in.

## Quick start

```bash
npm install
npm run dev
```

Open the printed local URL (typically http://localhost:5173). The app opens
directly to `/dashboard` — no login required.

## Tech stack

- React 19 + TypeScript + Vite
- Tailwind CSS
- React Router
- Recharts (charts)
- Leaflet + React-Leaflet (interactive map, OpenStreetMap tiles)
- Lucide React (icons)

## Pages

| Route              | Page                 |
|---------------------|---------------------|
| `/dashboard`         | Network overview: KPIs, charts, top critical areas |
| `/map`               | Interactive Leaflet map with filters and risk markers |
| `/area-insights`     | Deep dive on a selected area: root cause, recommendation, charts |
| `/recommendations`   | Prioritized recruitment table with sorting/filtering |
| `/what-if`           | Simulator for adding providers to an area/specialty |

The sidebar links all six pages together, and area selection (from the
dashboard table, the map, or recommendations) flows into Area Insights and
the What-if Simulator via `src/context/SelectedAreaContext.tsx`.

## Project structure

```
src/
  types/          TypeScript interfaces (Area, Recommendation, WhatIfResult, ...)
  data/            mockData.ts — the ONLY place raw demo records live
  services/api.ts  Promise-based data-fetch functions pages call into
  context/         SelectedAreaContext (shared selected-area state across pages)
  components/      Reusable UI: Sidebar, Header, KpiCard, RiskBadge, DataTable, ...
  pages/           The six routed pages
```

## Connecting a real backend later

Pages never import from `mockData.ts` directly for anything shown on
screen — they call functions in `src/services/api.ts`
(`getDashboardData()`, `getAreas()`, `getAreaDetails()`,
`getRecommendationsData()`, `getWhatIfPrediction()`). Each currently
resolves mock data wrapped in a `Promise`. To wire up FastAPI:

1. Replace each function body in `src/services/api.ts` with a `fetch()`
   call to the matching REST endpoint.
2. Keep the return types identical (they're defined in `src/types/index.ts`)
   — no page or component code needs to change.
3. Delete `src/data/mockData.ts` once the backend is transforming your real
   dataset into these same shapes.

`VITE_API_BASE_URL` is already read from the environment in `api.ts` for
when that day comes.

## Notes

- The What-if Simulator and Recommendations pages use simple, clearly
  documented mock formulas (see `computeWhatIf` in `mockData.ts`) — not a
  real ML model, per the current project scope.
