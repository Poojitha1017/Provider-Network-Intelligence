import logging
import os
import csv
from typing import Optional, Dict, Any, List
from app.db.supabase import get_supabase_admin_client, get_supabase_client
from app.schemas.provider import Provider, PaginatedProviderResponse

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


FALLBACK_PROVIDERS = [
    {
        "id": 1,
        "NPI": "1023094653",
        "PROVIDER_NAME": "JEFFREY D SEDER",
        "PRIMARY_SPECIALTY": "Cardiology",
        "STATE": "NC",
        "CITY": "SUPPLY",
        "ZIP": "284624094",
        "COUNTY_FIPS": "37019",
        "latitude": 33.987,
        "longitude": -78.265,
        "TELEHEALTH": True,
        "FACILITY_NAME": "Brunswick Medical",
        "COUNTY": "Brunswick County",
        "TOT_BENES": 327,
        "TOT_SRVCS": 1517.0,
        "BENE_AVG_RISK_SCRE": 1.5062,
        "TOTAL_UTILIZATION_EXACT": 88.5,
        "AVG_UTILIZATION_PERCENTILE": 75.0,
        "DISEASE": "Heart Disease",
    },
    {
        "id": 2,
        "NPI": "1073886875",
        "PROVIDER_NAME": "ANDREW THIBODEAUX",
        "PRIMARY_SPECIALTY": "Cardiology",
        "STATE": "TX",
        "CITY": "LONGVIEW",
        "ZIP": "75601",
        "COUNTY_FIPS": "48183",
        "latitude": 32.5007,
        "longitude": -94.7405,
        "TELEHEALTH": True,
        "FACILITY_NAME": "Longview Regional Medical Center",
        "COUNTY": "Gregg County",
        "TOT_BENES": 450,
        "TOT_SRVCS": 1200.0,
        "BENE_AVG_RISK_SCRE": 1.45,
        "TOTAL_UTILIZATION_EXACT": 92.1,
        "AVG_UTILIZATION_PERCENTILE": 85.0,
        "DISEASE": "Heart Disease",
    },
]

csv_prov_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "data", "UC05_PROVIDER_PREPROCESSED_FEATURED.csv")
if os.path.exists(csv_prov_path):
    try:
        loaded_provs = []
        from app.services.decision_service import get_fips_geo
        with open(csv_prov_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for idx, r in enumerate(reader):
                npi = str(r.get("NPI") or "")
                fips = str(r.get("COUNTY_FIPS") or "")
                geo_lat, geo_lng, city_name, state_name = get_fips_geo(fips, r.get("STATE"))
                
                lat = float(r["latitude"]) if r.get("latitude") is not None and r.get("latitude") != "" else geo_lat
                lng = float(r["longitude"]) if r.get("longitude") is not None and r.get("longitude") != "" else geo_lng
                
                loaded_provs.append({
                    "id": idx + 3,
                    "NPI": npi,
                    "PROVIDER_NAME": r.get("PROVIDER_NAME") or "",
                    "PRIMARY_SPECIALTY": r.get("PRIMARY_SPECIALTY") or "",
                    "STATE": r.get("STATE") or state_name,
                    "CITY": r.get("CITY") or city_name,
                    "ZIP": r.get("ZIP") or "",
                    "COUNTY_FIPS": fips,
                    "latitude": lat,
                    "longitude": lng,
                    "TELEHEALTH": r.get("TELEHEALTH_FLAG") == "1" or r.get("TELEHEALTH") == "True",
                    "FACILITY_NAME": r.get("FACILITY_NAME") or "Clinic",
                    "COUNTY": r.get("COUNTY") or "",
                    "TOT_BENES": int(float(r.get("TOT_BENES") or 0)),
                    "TOT_SRVCS": float(r.get("TOT_SRVCS") or 0.0),
                    "BENE_AVG_RISK_SCRE": float(r.get("BENE_AVG_RISK_SCRE") or 1.0),
                    "TOTAL_UTILIZATION_EXACT": float(r.get("TOTAL_UTILIZATION_EXACT") or 50.0),
                    "AVG_UTILIZATION_PERCENTILE": float(r.get("AVG_UTILIZATION_PERCENTILE") or 50.0),
                    "DISEASE": r.get("DISEASE") or "",
                })
        if loaded_provs:
            FALLBACK_PROVIDERS.extend(loaded_provs)
    except Exception as e:
        logging.getLogger("uvicorn.error").error(f"Error loading UC05_PROVIDER_PREPROCESSED_FEATURED.csv: {e}")


def map_db_provider_to_schema(r: Dict[str, Any]) -> Provider:
    raw_state = r.get("STATE") or r.get("state") or ""
    display_state = normalize_state(raw_state) or raw_state

    return Provider(
        id=r.get("id"),
        npi=str(r.get("NPI") or r.get("npi") or ""),
        provider_name=r.get("PROVIDER_NAME") or r.get("provider_name") or r.get("name") or "",
        primary_specialty=r.get("PRIMARY_SPECIALTY") or r.get("primary_specialty") or r.get("specialty") or "",
        secondary_specialty=r.get("SECONDARY_SPECIALTY") or r.get("secondary_specialty"),
        state=display_state,
        city=str(r.get("CITY") or r.get("city") or "").upper(),
        zip=str(r.get("ZIP") or r.get("zip") or ""),
        county=r.get("COUNTY") or r.get("county"),
        county_fips=str(r.get("COUNTY_FIPS") or r.get("county_fips") or ""),
        latitude=float(r["latitude"]) if r.get("latitude") is not None else None,
        longitude=float(r["longitude"]) if r.get("longitude") is not None else None,
        telehealth=bool(r.get("TELEHEALTH") if r.get("TELEHEALTH") is not None else r.get("telehealth", False)),
        facility_name=r.get("FACILITY_NAME") or r.get("facility_name"),
        tot_benes=int(r["TOT_BENES"]) if r.get("TOT_BENES") is not None else None,
        tot_srvcs=int(r["TOT_SRVCS"]) if r.get("TOT_SRVCS") is not None else None,
        bene_avg_risk_scre=float(r["BENE_AVG_RISK_SCRE"]) if r.get("BENE_AVG_RISK_SCRE") is not None else None,
        total_utilization_exact=float(r["TOTAL_UTILIZATION_EXACT"]) if r.get("TOTAL_UTILIZATION_EXACT") is not None else None,
        avg_utilization_percentile=float(r["AVG_UTILIZATION_PERCENTILE"]) if r.get("AVG_UTILIZATION_PERCENTILE") is not None else None,
        disease=r.get("DISEASE") or r.get("disease"),
    )


class ProviderService:
    @staticmethod
    def get_providers(
        county_fips: Optional[str] = None,
        state: Optional[str] = None,
        city: Optional[str] = None,
        specialty: Optional[str] = None,
        disease: Optional[str] = None,
        telehealth: Optional[bool] = None,
        page: int = 1,
        page_size: int = 20,
    ) -> PaginatedProviderResponse:
        """
        Retrieves matching providers from Supabase `providers` table.
        """
        client = get_supabase_admin_client() or get_supabase_client()
        records: List[Dict[str, Any]] = []
        total_count = 0

        page = max(1, page)
        page_size = max(1, min(100, page_size))
        start_idx = (page - 1) * page_size
        end_idx = start_idx + page_size - 1

        if client:
            try:
                query = client.table("providers").select("*", count="exact")

                if county_fips and county_fips.strip() and county_fips != "All Counties":
                    query = query.eq("COUNTY_FIPS", county_fips.strip())
                if state and state.strip() and state != "All States":
                    code = STATE_CODE_MAP.get(state.strip(), state.strip())
                    name = normalize_state(state.strip()) or state.strip()
                    query = query.or_(f"STATE.ilike.%{code}%,STATE.ilike.%{name}%")
                if city and city.strip() and city != "All Cities":
                    query = query.ilike("CITY", f"%{city.strip()}%")
                if specialty and specialty.strip() and specialty != "All Specialties":
                    query = query.ilike("PRIMARY_SPECIALTY", f"%{specialty.strip()}%")
                if disease and disease.strip() and disease != "All Diseases":
                    query = query.ilike("DISEASE", f"%{disease.strip()}%")
                if telehealth is not None:
                    query = query.eq("TELEHEALTH", telehealth)

                response = query.range(start_idx, end_idx).execute()
                records = response.data if response and response.data else []
                total_count = response.count if response and response.count is not None else len(records)
            except Exception as e:
                logger.error(f"Error querying providers table in Supabase: {e}")
                records = []

        if not records:
            fb = FALLBACK_PROVIDERS
            if county_fips and county_fips.strip() and county_fips != "All Counties":
                fb = [r for r in fb if str(r.get("COUNTY_FIPS")) == county_fips.strip()]
            if specialty and specialty.strip() and specialty != "All Specialties":
                fb = [r for r in fb if specialty.strip().lower() in str(r.get("PRIMARY_SPECIALTY", "")).lower()]
            if disease and disease.strip() and disease != "All Diseases":
                fb = [r for r in fb if disease.strip().lower() in str(r.get("DISEASE", "")).lower()]
            
            total_count = len(fb)
            records = fb[start_idx : start_idx + page_size]

        provider_objects = [map_db_provider_to_schema(r) for r in records]
        total_pages = max(1, (total_count + page_size - 1) // page_size)

        return PaginatedProviderResponse(
            total=total_count,
            page=page,
            page_size=page_size,
            total_pages=total_pages,
            providers=provider_objects,
        )


provider_service = ProviderService()
