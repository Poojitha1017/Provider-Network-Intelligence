import logging
from typing import Optional, List
from app.schemas.decision import RecommendationItem, RecommendationSummaryResponse, RecommendationsDataResponse
from app.services.decision_service import DecisionService
from app.services.simulation_service import simulation_service
from app.services.model_service import model_service
from app.schemas.simulation import WhatIfRequest

logger = logging.getLogger("uvicorn.error")


class RecommendationService:
    @staticmethod
    def get_recommendations(
        state: Optional[str] = None,
        specialty: Optional[str] = None,
        risk_level: Optional[str] = None,
    ) -> RecommendationsDataResponse:
        """
        Calculates and returns prioritized recruitment recommendations using the
        Stage 8 Rule-Based Action Classifier and Expected Impact Ranking.
        """
        # Fetch current dynamic map areas
        map_response = DecisionService.get_map_areas(
            state=state,
            specialty=specialty,
            risk_level=risk_level,
        )
        areas = map_response.areas

        # Sort primarily by Expected Impact Score (descending)
        sorted_areas = sorted(areas, key=lambda a: a.expectedImpactScore, reverse=True)

        items: List[RecommendationItem] = []
        for i, a in enumerate(sorted_areas):
            demand_tier = "high" if a.riskScore >= 70 else ("medium" if a.riskScore >= 45 else "low")

            # Stage 8 Rule-Based Classification (Image 2 - Step 12)
            action_text, rec_category = model_service.classify_action(
                risk_level=a.riskLevel,
                provider_count=a.providerSupply,
                estimated_patients=a.population,
                avg_travel_distance_km=a.avgTravelDistanceKm,
            )

            # Construct structured explainable reason
            if a.providerSupply == 0:
                reason = f"Zero {a.primarySpecialty.lower()} providers in network for {a.population:,} beneficiaries. Urgent {rec_category} recommended."
            elif a.avgTravelDistanceKm >= 28.0:
                reason = f"Average specialist distance is {a.avgTravelDistanceKm} km. Recommend {rec_category} to bridge travel barrier."
            else:
                reason = f"Severe patient-to-provider ratio under {a.primarySpecialty.lower()}. Action: {action_text} ({rec_category})."

            items.append(
                RecommendationItem(
                    rank=i + 1,
                    areaId=a.id,
                    areaName=a.name,
                    state=a.state,
                    specialty=a.primarySpecialty,
                    disease=a.diseases[0].disease if a.diseases else "Chronic Care",
                    riskScore=a.riskScore,
                    currentProviders=a.providerSupply,
                    providersNeeded=a.providersNeeded,
                    demand=demand_tier,
                    avgTravelDistanceKm=a.avgTravelDistanceKm,
                    expectedImpact=a.expectedImpact,
                    expectedImpactScore=a.expectedImpactScore,
                    confidenceScore=a.recommendationConfidencePct,
                    reason=reason,
                )
            )

        # Summary calculations
        critical_count = sum(1 for item in items if item.expectedImpact == "high")
        total_providers_needed = sum(item.providersNeeded for item in items)
        highest_risk = max((item.riskScore for item in items), default=0.0)

        # Calculate potential access improvement
        improvement_sum = 0.0
        for item in items[:15]:  # Compute simulation on top 15 priority areas for efficiency
            if item.providersNeeded > 0:
                sim = simulation_service.run_simulation(
                    WhatIfRequest(
                        county_fips=item.areaId,
                        specialty=item.specialty,
                        additional_providers=min(5, item.providersNeeded),
                    )
                )
                improvement_sum += sim.accessImprovementPct

        avg_improvement = round(improvement_sum / max(1, min(15, len(items))), 1) if items else 0.0

        summary = RecommendationSummaryResponse(
            criticalRecruitmentAreas=critical_count,
            totalProvidersRecommended=total_providers_needed,
            highestRiskPct=highest_risk,
            potentialAccessImprovementPct=avg_improvement,
        )

        return RecommendationsDataResponse(summary=summary, items=items)


recommendation_service = RecommendationService()
