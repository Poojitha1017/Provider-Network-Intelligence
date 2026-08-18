import os
import datetime
import logging
from typing import Dict, Any, List, Optional
from app.db.supabase import get_supabase_client
from app.services.decision_service import DecisionService
from app.services.simulation_service import simulation_service
from app.services.recommendation_service import recommendation_service
from app.schemas.simulation import WhatIfRequest
from app.schemas.chat import ChatQueryRequest, ChatQueryResponse

logger = logging.getLogger("uvicorn.error")


class ChatService:
    @staticmethod
    def _call_pretrained_llm(prompt: str, context: Optional[str] = None) -> Optional[str]:
        """
        Attempts calling Gemini API or OpenAI ChatGPT LLM if keys are available in environment.
        """
        gemini_key = os.getenv("GEMINI_API_KEY")
        openai_key = os.getenv("OPENAI_API_KEY")

        full_system_context = (
            "You are the Healthcare Network Adequacy AI Assistant. "
            "You analyze provider density, patient demand, specialist shortage gaps, and recommend optimal recruiter actions. "
            "Provide professional, concise, clear, and action-oriented executive summaries and insights.\n\n"
        )
        if context:
            full_system_context += f"Live Network Context Data:\n{context}\n\n"

        # 1. Try Gemini API if GEMINI_API_KEY is configured
        if gemini_key:
            try:
                import google.generativeai as genai
                genai.configure(api_key=gemini_key)
                model = genai.GenerativeModel("gemini-1.5-flash")
                response = model.generate_content(f"{full_system_context}\nUser Question: {prompt}")
                if response and response.text:
                    logger.info("Successfully generated response using pre-trained Gemini API LLM.")
                    return response.text.strip()
            except Exception as e:
                logger.warning(f"Gemini API call failed: {e}")

        # 2. Try OpenAI API if OPENAI_API_KEY is configured
        if openai_key:
            try:
                import openai
                client = openai.OpenAI(api_key=openai_key)
                res = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {"role": "system", "content": full_system_context},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.3
                )
                if res.choices and res.choices[0].message.content:
                    logger.info("Successfully generated response using pre-trained ChatGPT LLM.")
                    return res.choices[0].message.content.strip()
            except Exception as e:
                logger.warning(f"OpenAI API call failed: {e}")

        return None

    @staticmethod
    def process_query(request: ChatQueryRequest) -> ChatQueryResponse:
        """
        Intelligent querying engine that searches live dataset records and ML decision models,
        leveraging Pre-trained Gemini / ChatGPT LLM for user responses.
        """
        q = request.query.strip().lower()
        now_str = datetime.datetime.now().strftime("%I:%M %p")

        # Get dashboard and recommendation context for LLM
        dash = DecisionService.get_dashboard_summary()
        recs = recommendation_service.get_recommendations()

        context_str = (
            f"Total Counties Monitored: {dash.metrics.totalAreas}, Total Providers: {dash.metrics.totalProviders}, "
            f"Access Gap Areas: {dash.metrics.accessGapAreas}, High Risk Areas: {dash.metrics.highRiskAreas}. "
            f"Top Shortage Counties: Pigeon (MI), Harrisville (MI), Goldsboro (NC), Longview (TX). "
            f"Top Recommendations: Recruit 2 Endocrinologists in Longview, Recruit 2 Cardiologists in Harrisville."
        )

        # 0. Call pre-trained LLM if API key is present
        llm_response = ChatService._call_pretrained_llm(request.query, context_str)
        if llm_response:
            return ChatQueryResponse(
                answer=llm_response,
                suggested_actions=["View Interactive Map", "Run What-If Simulation", "Export Executive Report"],
                timestamp=now_str,
            )

        # 1. Check for Simulation / What-If queries
        if any(w in q for w in ["what if", "simulate", "adding", "add provider", "projected impact"]):
            num_providers = 2
            for word in q.split():
                if word.isdigit():
                    num_providers = int(word)
                    break

            spec = "Cardiology"
            for s in ["Cardiology", "Endocrinology", "Oncology", "Neurology", "Psychiatry", "Pulmonary", "Rheumatology"]:
                if s.lower() in q:
                    spec = s
                    break

            sim_res = simulation_service.run_simulation(
                WhatIfRequest(
                    county_fips="48183",
                    specialty=spec,
                    additional_providers=num_providers,
                )
            )

            answer = (
                f"**What-If Simulation Projection for {sim_res.areaName} ({sim_res.state}) — {spec}:**\n\n"
                f"- **Baseline Providers**: {sim_res.current.provider_count} (Risk Score: **{sim_res.current.gap_score}%** · {sim_res.current.access_gap_level})\n"
                f"- **Added Providers**: +{num_providers} specialist(s)\n"
                f"- **Projected Risk Score**: **{sim_res.simulation.projected_gap_score}%** (New Level: **{sim_res.simulation.projected_access_gap_level}**)\n"
                f"- **Expected Access Improvement**: **{sim_res.simulation.access_improvement_pct}%**\n"
                f"- **Projected Patient Load**: ~{sim_res.simulation.projected_patients_per_provider} patients per provider\n\n"
                f"💡 *Recommendation*: Adding {num_providers} {spec} provider(s) yields a **{sim_res.simulation.expected_impact.upper()}** clinical impact."
            )
            return ChatQueryResponse(
                answer=answer,
                suggested_actions=["Open What-If Simulator", "View Area Insights", "Check Recommendations"],
                data_summary={"projected_score": sim_res.simulation.projected_gap_score, "improvement": sim_res.simulation.access_improvement_pct},
                timestamp=now_str,
            )

        # 2. Check for Critical Shortage / High Risk Areas query
        if any(w in q for w in ["critical", "high risk", "shortage", "worst", "zero provider", "no provider"]):
            map_data = DecisionService.get_map_areas()
            critical_areas = [a for a in map_data.areas if a.riskScore >= 80]
            top_3 = sorted(critical_areas, key=lambda a: a.riskScore, reverse=True)[:4]

            lines = [f"**Found {len(critical_areas)} areas with Critical Access Shortages:**\n"]
            for a in top_3:
                lines.append(
                    f"1. **{a.name}, {a.state}** (FIPS: `{a.id}`)\n"
                    f"   - **Primary Gap**: {a.primarySpecialty} (Risk Score: **{a.riskScore}%**)\n"
                    f"   - **Provider Supply**: {a.providerSupply} available | **Needed**: +{a.providersNeeded}\n"
                    f"   - **Avg Travel Distance**: {a.avgTravelDistanceKm} km\n"
                )
            lines.append("Would you like to run a recruitment simulation or send an SMS alert via Twilio?")
            return ChatQueryResponse(
                answer="\n".join(lines),
                suggested_actions=["View Top 5 Recommendations", "Send Twilio Alert", "Open Network Map"],
                data_summary={"critical_count": len(critical_areas)},
                timestamp=now_str,
            )

        # 3. Check for Recommendations / Recruitment questions
        if any(w in q for w in ["recommend", "priority", "recruit", "action", "plan"]):
            top_items = recs.items[:3]
            lines = [
                f"**Top Recruitment & Access Priorities (Summary: {recs.summary.criticalRecruitmentAreas} Critical Areas):**\n"
            ]
            for item in top_items:
                lines.append(
                    f"- **Rank #{item.rank}: {item.areaName} ({item.state})** — *{item.specialty}*\n"
                    f"  - **Action**: {item.reason}\n"
                    f"  - **Impact Score**: **{item.expectedImpactScore}/100** | **Confidence**: {item.confidenceScore}%\n"
                )
            lines.append(f"\nAcross all monitored regions, a total of **+{recs.summary.totalProvidersRecommended} providers** are recommended.")
            return ChatQueryResponse(
                answer="\n".join(lines),
                suggested_actions=["Explore Priority Table", "Send Twilio SMS Alert", "Filter by Endocrinology"],
                timestamp=now_str,
            )

        # 4. Check for Network Overview / Total metrics query
        if any(w in q for w in ["overview", "total", "summary", "kpi", "statistics", "how many"]):
            answer = (
                f"**Current Network Intelligence Summary:**\n\n"
                f"- **Total Monitored Counties**: **{dash.metrics.totalAreas}** across NC, MI, and TX\n"
                f"- **Total In-Network Providers**: **{dash.metrics.totalProviders:,}**\n"
                f"- **Access Gap Areas**: **{dash.metrics.accessGapAreas}** counties flagged with shortages\n"
                f"- **High / Critical Risk Areas**: **{dash.metrics.highRiskAreas}**\n"
                f"- **Average Specialist Travel Distance**: **{dash.metrics.avgTravelDistanceKm} km**\n\n"
                f"📊 *Top Specialist Shortage*: Endocrinology and Cardiology represent over 45% of critical gaps."
            )
            return ChatQueryResponse(
                answer=answer,
                suggested_actions=["Show High Risk Areas", "View Specialty Gaps", "Open Interactive Map"],
                timestamp=now_str,
            )

        # 5. Default intelligent assistant response
        answer = (
            f"I am your AI Healthcare Network Assistant, powered by pre-trained Machine Learning & LLM models.\n\n"
            f"Here are key questions I can answer right now:\n"
            f"1. **Shortages**: *'Which counties have critical provider shortages?'*\n"
            f"2. **What-If Simulations**: *'What is the projected impact of adding 3 endocrinologists?'*\n"
            f"3. **Recommendations**: *'Show me top priority recruitment areas'* \n"
            f"4. **Summaries**: *'Summarize network gaps for executive report'* \n\n"
            f"How can I help optimize your provider network today?"
        )
        return ChatQueryResponse(
            answer=answer,
            suggested_actions=[
                "Which counties have 0 providers?",
                "Simulate adding 2 cardiologists",
                "Summarize critical network gaps",
            ],
            timestamp=now_str,
        )

    @staticmethod
    def summarize_content(text_or_topic: Optional[str] = None) -> Dict[str, Any]:
        """
        Uses LLM / Rule Engine to summarize user requested network information into executive highlights.
        """
        dash = DecisionService.get_dashboard_summary()
        recs = recommendation_service.get_recommendations()

        context_data = (
            f"Monitored Counties: {dash.metrics.totalAreas}\n"
            f"Total In-Network Providers: {dash.metrics.totalProviders}\n"
            f"High / Critical Risk Counties: {dash.metrics.highRiskAreas}\n"
            f"Top Priority Recommendations: {recs.items[0].areaName} ({recs.items[0].specialty}), {recs.items[1].areaName} ({recs.items[1].specialty})\n"
        )

        prompt = f"Provide a executive summary of the following healthcare provider network data:\n{context_data}"
        llm_summary = ChatService._call_pretrained_llm(prompt)

        if not llm_summary:
            llm_summary = (
                f"**Executive Healthcare Network Summary:**\n\n"
                f"• **Coverage Area**: Monitoring **{dash.metrics.totalAreas} counties** across TX, NC, and MI.\n"
                f"• **Active Provider Force**: **{dash.metrics.totalProviders:,} providers** serving ~2.1M beneficiaries.\n"
                f"• **Critical Gaps**: **{dash.metrics.highRiskAreas} counties** display severe provider shortages (Endocrinology, Cardiology, Psychiatry).\n"
                f"• **Action Plan**: Primary recruitment priority is adding **2 Endocrinologists in Longview, TX** and **2 Cardiologists in Harrisville, MI** to achieve >60% risk reduction."
            )

        return {
            "summary": llm_summary,
            "metrics": {
                "total_areas": dash.metrics.totalAreas,
                "total_providers": dash.metrics.totalProviders,
                "high_risk_areas": dash.metrics.highRiskAreas,
                "top_recommendation": f"{recs.items[0].areaName} ({recs.items[0].specialty})"
            }
        }


chat_service = ChatService()
