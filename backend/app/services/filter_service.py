import logging
from typing import Optional, Dict, Any, List
from app.db.supabase import get_supabase_admin_client, get_supabase_client
from app.schemas.filters import FilterOptionsResponse, CountyOption

logger = logging.getLogger("uvicorn.error")

STATE_MAP = {
    "TX": "Texas",
    "TEXAS": "Texas",
    "NC": "North Carolina",
    "NORTH CAROLINA": "North Carolina",
    "MI": "Michigan",
    "MICHIGAN": "Michigan",
}

STATE_CODE_MAP = {
    "Texas": "TX",
    "North Carolina": "NC",
    "Michigan": "MI",
}


def normalize_state(val: Optional[str]) -> Optional[str]:
    if not val:
        return None
    cleaned = val.strip()
    return STATE_MAP.get(cleaned.upper(), cleaned)


from app.services.decision_service import FALLBACK_DECISIONS

def get_fallback_filter_records():
    from app.services.decision_service import FALLBACK_DECISIONS
    return [
        {
            "state": r.get("STATEDESC") or r.get("state"),
            "city": r.get("CITY") or r.get("city"),
            "county_fips": r.get("COUNTY_FIPS") or r.get("county_fips"),
            "specialty": r.get("REQUIRED_SPECIALTY") or r.get("specialty"),
            "disease": r.get("DISEASE") or r.get("disease"),
            "risk_level": r.get("ACCESS_GAP_LEVEL") or r.get("risk_level"),
        }
        for r in FALLBACK_DECISIONS
    ]


class FilterService:
    @staticmethod
    def get_options(
        county_fips: Optional[str] = None,
        city: Optional[str] = None,
        disease: Optional[str] = None,
        specialty: Optional[str] = None,
        risk_level: Optional[str] = None,
        state: Optional[str] = None,
    ) -> FilterOptionsResponse:
        """
        Dynamically queries `public.uc05_filter_options` in Supabase with parameter filtering.
        """
        client = get_supabase_admin_client() or get_supabase_client()
        records: List[Dict[str, Any]] = []

        if client:
            try:
                query = client.table("uc05_filter_options").select(
                    "state, county, disease, specialty, risk_level, county_fips"
                )

                if state and state.strip() and state != "All States":
                    code = STATE_CODE_MAP.get(state.strip(), state.strip())
                    name = normalize_state(state.strip()) or state.strip()
                    # Match state code or full name
                    query = query.or_(f"state.ilike.%{code}%,state.ilike.%{name}%")
                if county_fips and county_fips.strip() and county_fips != "All Counties":
                    query = query.eq("county_fips", county_fips.strip())
                if city and city.strip() and city != "All Cities":
                    query = query.ilike("county", f"%{city.strip()}%")
                if disease and disease.strip() and disease != "All Diseases":
                    query = query.ilike("disease", f"%{disease.strip()}%")
                if specialty and specialty.strip() and specialty != "All Specialties":
                    query = query.ilike("specialty", f"%{specialty.strip()}%")
                if risk_level and risk_level.strip() and risk_level != "All":
                    query = query.ilike("risk_level", f"%{risk_level.strip()}%")

                response = query.limit(2000).execute()
                raw_data = response.data if response and response.data else []
                records = [
                    {
                        "state": r.get("state"),
                        "city": r.get("county"),
                        "disease": r.get("disease"),
                        "specialty": r.get("specialty"),
                        "risk_level": r.get("risk_level"),
                        "county_fips": r.get("county_fips"),
                    }
                    for r in raw_data
                ]
            except Exception as e:
                logger.error(f"Error querying uc05_filter_options in Supabase: {e}")
                records = []

        if not records:
            # Filter fallback records matching criteria
            records = get_fallback_filter_records()
            if state and state.strip() and state != "All States":
                norm = normalize_state(state.strip())
                records = [r for r in records if normalize_state(r.get("state")) == norm]
            if county_fips and county_fips.strip() and county_fips != "All Counties":
                records = [r for r in records if r.get("county_fips") == county_fips.strip()]
            if city and city.strip() and city != "All Cities":
                records = [r for r in records if str(r.get("city", "")).lower() == city.strip().lower()]
            if disease and disease.strip() and disease != "All Diseases":
                records = [r for r in records if str(r.get("disease", "")).lower() == disease.strip().lower()]
            if specialty and specialty.strip() and specialty != "All Specialties":
                records = [r for r in records if str(r.get("specialty", "")).lower() == specialty.strip().lower()]
            if risk_level and risk_level.strip() and risk_level != "All":
                records = [r for r in records if risk_level.strip().lower() in str(r.get("risk_level", "")).lower()]

        # Extract unique sorted lists
        states = sorted(list({normalize_state(r["state"]) for r in records if r.get("state")}))
        cities = sorted(list({str(r["city"]).upper() for r in records if r.get("city")}))
        diseases = sorted(list({str(r["disease"]) for r in records if r.get("disease")}))
        specialties = sorted(list({str(r["specialty"]) for r in records if r.get("specialty")}))
        risk_levels = sorted(list({str(r["risk_level"]) for r in records if r.get("risk_level")}))
        county_fips_list = sorted(list({str(r["county_fips"]) for r in records if r.get("county_fips")}))

        # County objects with FIPS and City/County name
        counties_map: Dict[str, CountyOption] = {}
        for r in records:
            fips = r.get("county_fips")
            if fips and fips not in counties_map:
                counties_map[fips] = CountyOption(
                    county_fips=str(fips),
                    county_name=r.get("city") or str(fips),
                    state=normalize_state(r.get("state")),
                )

        return FilterOptionsResponse(
            states=states,
            cities=cities,
            county_fips_list=county_fips_list,
            counties=list(counties_map.values()),
            diseases=diseases,
            specialties=specialties,
            risk_levels=risk_levels,
        )


filter_service = FilterService()
