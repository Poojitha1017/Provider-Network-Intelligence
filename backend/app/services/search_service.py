import logging
from typing import Optional, Dict, Any, List
from app.db.supabase import get_supabase_client
from app.schemas.search import SearchResultItem, PaginatedSearchResponse
from app.services.decision_service import FALLBACK_DECISIONS, COUNTY_COORDS_MAP
from app.services.model_service import model_service

logger = logging.getLogger("uvicorn.error")


class SearchService:
    @staticmethod
    def search(
        county_fips: Optional[str] = None,
        state: Optional[str] = None,
        city: Optional[str] = None,
        disease: Optional[str] = None,
        specialty: Optional[str] = None,
        risk_level: Optional[str] = None,
        page: int = 1,
        page_size: int = 20,
    ) -> PaginatedSearchResponse:
        """
        Unified search endpoint across decision intelligence and provider access records.
        """
        client = get_supabase_client()
        records: List[Dict[str, Any]] = []
        total_count = 0

        page = max(1, page)
        page_size = max(1, min(100, page_size))
        start_idx = (page - 1) * page_size
        end_idx = start_idx + page_size - 1

        if client:
            try:
                query = client.table("decision").select("*", count="exact")

                if county_fips and county_fips.strip() and county_fips != "All Counties":
                    query = query.eq("COUNTY_FIPS", county_fips.strip())
                if state and state.strip() and state != "All States":
                    query = query.ilike("STATEDESC", f"%{state.strip()}%")
                if specialty and specialty.strip() and specialty != "All Specialties":
                    query = query.ilike("REQUIRED_SPECIALTY", f"%{specialty.strip()}%")
                if risk_level and risk_level.strip() and risk_level != "All":
                    query = query.ilike("ACCESS_GAP_LEVEL", f"%{risk_level.strip()}%")

                response = query.range(start_idx, end_idx).execute()
                records = response.data if response and response.data else []
                total_count = response.count if response and response.count is not None else len(records)
            except Exception as e:
                logger.error(f"Error executing search query in Supabase: {e}")
                records = []

        if not records:
            fb = FALLBACK_DECISIONS
            if county_fips and county_fips.strip() and county_fips != "All Counties":
                fb = [r for r in fb if str(r.get("COUNTY_FIPS")) == county_fips.strip()]
            if state and state.strip() and state != "All States":
                fb = [r for r in fb if state.strip().lower() in str(r.get("STATEDESC", "")).lower()]
            if city and city.strip() and city != "All Cities":
                fb = [r for r in fb if city.strip().lower() in str(r.get("CITY", "")).lower()]
            if specialty and specialty.strip() and specialty != "All Specialties":
                fb = [r for r in fb if specialty.strip().lower() in str(r.get("REQUIRED_SPECIALTY", "")).lower()]
            if disease and disease.strip() and disease != "All Diseases":
                fb = [r for r in fb if disease.strip().lower() in str(r.get("DISEASE", "")).lower()]
            if risk_level and risk_level.strip() and risk_level != "All":
                fb = [r for r in fb if risk_level.strip().lower() in str(r.get("ACCESS_GAP_LEVEL", "")).lower()]

            total_count = len(fb)
            records = fb[start_idx : start_idx + page_size]

        results: List[SearchResultItem] = []
        for r in records:
            fips_str = str(r.get("COUNTY_FIPS") or "")
            geo_info = COUNTY_COORDS_MAP.get(fips_str)
            city_val = r.get("CITY") or (geo_info[2] if geo_info else None)
            score = float(r.get("GAP_SCORE") or 50.0)
            level = str(r.get("ACCESS_GAP_LEVEL") or model_service.score_to_gap_level_str(score))
            results.append(
                SearchResultItem(
                    county_fips=fips_str,
                    state=r.get("STATEDESC") or (geo_info[3] if geo_info else r.get("state")),
                    city=city_val,
                    disease=r.get("DISEASE") or r.get("disease") or "Chronic Conditions",
                    specialty=r.get("REQUIRED_SPECIALTY") or r.get("specialty"),
                    risk_level=level,
                    risk_score=score,
                    provider_count=int(r["PROVIDER_COUNT"]) if r.get("PROVIDER_COUNT") is not None else None,
                    estimated_patients=int(r["ESTIMATED_PATIENTS"]) if r.get("ESTIMATED_PATIENTS") is not None else None,
                    patients_per_provider=float(r["PATIENTS_PER_PROVIDER"]) if r.get("PATIENTS_PER_PROVIDER") is not None else None,
                    gap_ratio=float(r["GAP_RATIO"]) if r.get("GAP_RATIO") is not None else None,
                    access_gap_level=level,
                )
            )

        total_pages = max(1, (total_count + page_size - 1) // page_size)
        return PaginatedSearchResponse(
            total=total_count,
            page=page,
            page_size=page_size,
            total_pages=total_pages,
            results=results,
        )


search_service = SearchService()
