# UC05 — Healthcare Provider Access & Decision Intelligence Backend

FastAPI backend integrated with Supabase PostgreSQL and React + Vite frontend for UC05 Provider Network Intelligence.

## Requirements
- Python 3.10+
- Dependencies listed in `requirements.txt`

## Setup & Running

1. **Configure Environment:**
   Edit `.env` (or copy `.env.example`):
   ```bash
   SUPABASE_URL=https://your-project.supabase.co
   SUPABASE_ANON_KEY=your-anon-key
   SUPABASE_SERVICE_ROLE_KEY=your-service-role-key
   ```

2. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Start FastAPI Development Server:**
   ```bash
   uvicorn app.main:app --reload --port 8000
   ```

4. **Interactive Swagger Documentation:**
   Open [http://localhost:8000/docs](http://localhost:8000/docs) in your browser.

## Key API Endpoints
- `GET /health` — Health and Supabase connection status
- `GET /api/v1/filters/options` — Dynamic dependent filter options
- `GET /api/v1/search` — Search access gap and provider intelligence
- `GET /api/v1/providers` — In-network providers lookup
- `GET /api/v1/access-gaps` — Decision access gap metrics
- `GET /api/v1/dashboard/summary` — Network overview KPIs and distribution
- `GET /api/v1/map/areas` — Dynamic map markers and per-disease breakdowns
- `POST /api/v1/simulation/what-if` — Non-destructive what-if scenario simulator
- `GET /api/v1/recommendations` — Prioritized recruitment recommendations
- `POST /api/v1/auth/signup` / `POST /api/v1/auth/login` — Authentication via Supabase
