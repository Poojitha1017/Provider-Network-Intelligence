import logging
from typing import Optional, Dict, Any
from app.db.supabase import get_supabase_admin_client, get_supabase_client
from app.schemas.simulation import WhatIfRequest, WhatIfResponse, WhatIfCurrent, WhatIfProjection, WhatIfCurvePoint
from app.services.model_service import model_service
from app.services.decision_service import FALLBACK_DECISIONS, COUNTY_COORDS_MAP

logger = logging.getLogger("uvicorn.error")


class SimulationService:
    @staticmethod
    def run_simulation(request: WhatIfRequest) -> WhatIfResponse:
        """
        Runs non-destructive What-if scenario analysis for adding providers to a county/specialty.
        """
        county_fips = (request.county_fips or request.areaId or "48183").strip()
        specialty = request.specialty.strip()
        additional_providers = request.additional_providers if request.additional_providers is not None else (request.providersToAdd or 0)
        additional_providers = max(0, min(20, additional_providers))

        client = get_supabase_admin_client() or get_supabase_client()
        matched_row: Optional[Dict[str, Any]] = None

        if client:
            try:
                # Query decision table for baseline exact match
                query = client.table("decision").select("*").eq("COUNTY_FIPS", county_fips)
                if specialty:
                    query = query.ilike("REQUIRED_SPECIALTY", f"%{specialty}%")
                response = query.limit(1).execute()
                if response and response.data:
                    matched_row = response.data[0]
            except Exception as e:
                logger.error(f"Error querying baseline for simulation: {e}")

        # Dynamic lookup from providers table if not in decision table
        if not matched_row and client:
            try:
                p_query = client.table("providers").select("NPI,TOT_BENES").eq("COUNTY_FIPS", county_fips)
                if specialty:
                    p_query = p_query.ilike("PRIMARY_SPECIALTY", f"%{specialty}%")
                p_resp = p_query.execute()
                if p_resp and p_resp.data:
                    prov_count = len(p_resp.data)
                    tot_benes = sum(int(row.get("TOT_BENES") or 0) for row in p_resp.data)
                    if tot_benes == 0:
                        tot_benes = 1200 * max(1, prov_count)
                    
                    # Compute baseline gap score
                    calculated_score = model_service.calculate_gap_score(
                        provider_count=prov_count,
                        estimated_patients=tot_benes,
                        specialty=specialty,
                    )
                    calculated_level = model_service.score_to_gap_level_str(calculated_score, prov_count)
                    
                    # Resolve geography
                    geo_info = COUNTY_COORDS_MAP.get(county_fips)
                    area_name = geo_info[2] if geo_info else f"County {county_fips}"
                    state_name = geo_info[3] if geo_info else "Texas"
                    
                    matched_row = {
                        "COUNTY_FIPS": county_fips,
                        "CITY": area_name,
                        "STATEDESC": state_name,
                        "REQUIRED_SPECIALTY": specialty,
                        "PROVIDER_COUNT": prov_count,
                        "ESTIMATED_PATIENTS": tot_benes,
                        "GAP_SCORE": calculated_score,
                        "ACCESS_GAP_LEVEL": calculated_level,
                    }
            except Exception as e:
                logger.error(f"Error dynamically building baseline from providers: {e}")

        if not matched_row:
            # Look up in fallback decisions
            matched_row = next(
                (r for r in FALLBACK_DECISIONS if r.get("COUNTY_FIPS") == county_fips),
                FALLBACK_DECISIONS[0],
            )

        # Baseline metrics
        current_providers = int(matched_row.get("PROVIDER_COUNT") or 0)
        estimated_patients = int(matched_row.get("ESTIMATED_PATIENTS") or 5000)
        current_patients_per_provider = float(
            matched_row.get("PATIENTS_PER_PROVIDER") or (estimated_patients / max(1, current_providers))
        )
        current_gap_score = float(matched_row.get("GAP_SCORE") or 85.0)
        current_gap_level = str(
            matched_row.get("ACCESS_GAP_LEVEL") or model_service.score_to_gap_level_str(current_gap_score, current_providers)
        )
        geo_info = COUNTY_COORDS_MAP.get(county_fips)
        area_name = str(matched_row.get("CITY") or (geo_info[2] if geo_info else f"County {county_fips}"))
        state_name = str(matched_row.get("STATEDESC") or (geo_info[3] if geo_info else "Texas"))

        # Run model simulation
        sim_calc = model_service.compute_simulation(
            current_providers=current_providers,
            estimated_patients=estimated_patients,
            specialty=specialty,
            additional_providers=additional_providers,
            current_gap_score=current_gap_score,
        )

        current_obj = WhatIfCurrent(
            provider_count=current_providers,
            estimated_patients=estimated_patients,
            patients_per_provider=round(current_patients_per_provider, 1),
            gap_score=current_gap_score,
            access_gap_level=current_gap_level,
        )

        projection_obj = WhatIfProjection(
            additional_providers=additional_providers,
            projected_provider_count=sim_calc["projected_provider_count"],
            projected_patients_per_provider=sim_calc["projected_patients_per_provider"],
            projected_gap_score=sim_calc["projected_gap_score"],
            projected_access_gap_level=sim_calc["projected_access_gap_level"],
            access_improvement_pct=sim_calc["access_improvement_pct"],
            expected_impact=sim_calc["expected_impact"],
        )

        curve_points = [
            WhatIfCurvePoint(
                providersAdded=p["providersAdded"],
                predictedRiskScore=p["predictedRiskScore"],
            )
            for p in sim_calc["curve"]
        ]

        return WhatIfResponse(
            county_fips=county_fips,
            areaId=county_fips,
            areaName=area_name,
            state=state_name,
            specialty=specialty,
            disease=request.disease or matched_row.get("DISEASE"),
            current=current_obj,
            simulation=projection_obj,
            currentProviders=current_providers,
            providersToAdd=additional_providers,
            newProviderCount=sim_calc["projected_provider_count"],
            currentRiskScore=current_gap_score,
            predictedRiskScore=sim_calc["projected_gap_score"],
            accessImprovementPct=sim_calc["access_improvement_pct"],
            predictedAccessGap=sim_calc["predicted_risk_level"],
            expectedImpact=sim_calc["expected_impact"],
            curve=curve_points,
        )


simulation_service = SimulationService()
