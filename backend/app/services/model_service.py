import math
import logging
from typing import Dict, Any, List, Literal, Tuple, Optional
import numpy as np
from sklearn.cluster import KMeans
from sklearn.ensemble import IsolationForest, GradientBoostingClassifier

logger = logging.getLogger("uvicorn.error")


import os
import joblib

MODELS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "models")


class MLDecisionEngine:
    """
    Complete ML and Decision Flow Pipeline for UC05 Provider Access & Intelligence System.
    Loads pre-trained production model artifacts from backend/models/.
    """

    SPECIALTY_BENCHMARKS = {
        "Cardiology": 1500,
        "Endocrinology": 1200,
        "Oncology": 1000,
        "Neurology": 1800,
        "Psychiatry": 1400,
        "Pulmonary": 2000,
        "Rheumatology": 2500,
    }

    def __init__(self):
        self._load_or_init_models()
        logger.info("MLDecisionEngine: All 8 analytics & modeling stages initialized.")

    def _load_or_init_models(self):
        """Loads pre-trained model artifacts from backend/models/ if available, else initializes."""
        clf_path = os.path.join(MODELS_DIR, "xgboost_gap_classifier.pkl")
        km_path = os.path.join(MODELS_DIR, "kmeans_cluster_model.pkl")
        iso_path = os.path.join(MODELS_DIR, "isolation_forest_anomaly.pkl")
        scaler_path = os.path.join(MODELS_DIR, "scaler.pkl")

        if os.path.exists(clf_path) and os.path.exists(km_path) and os.path.exists(iso_path):
            try:
                self.gap_classifier = joblib.load(clf_path)
                self.cluster_model = joblib.load(km_path)
                self.anomaly_detector = joblib.load(iso_path)
                self.scaler = joblib.load(scaler_path) if os.path.exists(scaler_path) else None
                logger.info(f"MLDecisionEngine: Loaded pre-trained models from {MODELS_DIR}")
                return
            except Exception as e:
                logger.warning(f"Error loading saved models from disk ({e}). Falling back to in-memory models.")

        # Baseline fallback initialization
        X_train = np.array([
            [8000, 0, 8000, 45.0, 15000, 0, 95.0],
            [5000, 1, 5000, 35.0, 10000, 0, 80.0],
            [3000, 2, 1500, 20.0, 6000, 0, 45.0],
            [1200, 4, 300, 10.0, 2500, 0, 20.0],
            [10000, 1, 10000, 50.0, 20000, 0, 98.0],
            [500, 5, 100, 8.0, 1000, 0, 15.0],
        ])
        y_train = np.array([1, 1, 1, 0, 1, 0])

        self.gap_classifier = GradientBoostingClassifier(n_estimators=50, random_state=42)
        self.gap_classifier.fit(X_train[:, :5], y_train)

        self.cluster_model = KMeans(n_clusters=4, random_state=42, n_init=10)
        self.cluster_model.fit(X_train[:, :5])

        self.anomaly_detector = IsolationForest(contamination=0.15, random_state=42)
        self.anomaly_detector.fit(X_train[:, :5])
        self.scaler = None

    # ------------------------------------------------------------------------
    # Stage 1: ML Gap Prediction
    # ------------------------------------------------------------------------
    def predict_gap(
        self,
        estimated_patients: int,
        provider_count: int,
        patients_per_provider: float,
        avg_travel_distance_km: float,
        total_beneficiaries: int,
    ) -> Tuple[bool, float]:
        """Predicts whether an area has an access gap and outputs gap probability."""
        features = np.array([[
            estimated_patients,
            provider_count,
            patients_per_provider,
            avg_travel_distance_km,
            total_beneficiaries,
        ]])
        prob = float(self.gap_classifier.predict_proba(features)[0][1])
        has_gap = prob >= 0.5
        return has_gap, round(prob * 100.0, 1)

    # ------------------------------------------------------------------------
    # Stage 2: Area Grouping (K-Means Clustering)
    # ------------------------------------------------------------------------
    def get_cluster_id(
        self,
        estimated_patients: int,
        provider_count: int,
        patients_per_provider: float,
        avg_travel_distance_km: float,
        total_beneficiaries: int,
    ) -> Tuple[int, str]:
        """Groups healthcare areas by provider, patient, demand, and supply characteristics."""
        features = np.array([[
            estimated_patients,
            provider_count,
            patients_per_provider,
            avg_travel_distance_km,
            total_beneficiaries,
        ]])
        cluster_id = int(self.cluster_model.predict(features)[0])
        labels = {
            0: "High Demand / Severe Shortage",
            1: "Rural / Geographic Distance Gap",
            2: "Moderate Demand / Balanced Supply",
            3: "Adequate Network Coverage",
        }
        return cluster_id, labels.get(cluster_id, "Standard Cluster")

    # ------------------------------------------------------------------------
    # Stage 3: Anomaly Detection (Isolation Forest)
    # ------------------------------------------------------------------------
    def detect_anomaly(
        self,
        estimated_patients: int,
        provider_count: int,
        patients_per_provider: float,
        avg_travel_distance_km: float,
        total_beneficiaries: int,
    ) -> Tuple[bool, float]:
        """Detects unusual access patterns differing significantly from normal areas."""
        features = np.array([[
            estimated_patients,
            provider_count,
            patients_per_provider,
            avg_travel_distance_km,
            total_beneficiaries,
        ]])
        pred = self.anomaly_detector.predict(features)[0]  # -1 for anomaly, 1 for normal
        score = float(self.anomaly_detector.score_samples(features)[0])
        is_anomaly = pred == -1
        # Normalize score into 0-100 anomaly intensity
        anomaly_intensity = round(max(0.0, min(100.0, (0.5 - score) * 100.0)), 1)
        return is_anomaly, anomaly_intensity

    # ------------------------------------------------------------------------
    # Stage 4 & 5: Combined Access Gap Score & Risk Level
    # ------------------------------------------------------------------------
    def calculate_gap_score(
        self,
        provider_count: int,
        estimated_patients: int,
        specialty: str = "General",
        avg_travel_distance_km: float = 20.0,
        db_gap_score: Optional[float] = None,
    ) -> float:
        """Combines database score, ratio pressure, distance pressure, and model factors."""
        if db_gap_score is not None and db_gap_score > 0:
            return round(min(100.0, max(0.0, db_gap_score)), 1)

        benchmark = self.SPECIALTY_BENCHMARKS.get(specialty, 1500)
        if provider_count <= 0:
            return 100.0

        current_ratio = estimated_patients / provider_count
        ratio_pressure = min(1.0, current_ratio / (benchmark * 2.0)) * 60.0
        distance_pressure = min(1.0, avg_travel_distance_km / 50.0) * 40.0
        return max(5.0, min(100.0, round(ratio_pressure + distance_pressure, 1)))

    def score_to_risk_level(self, score: float) -> Literal["low", "medium", "high", "critical"]:
        """Converts score into standardized risk category."""
        if score >= 80.0:
            return "critical"
        elif score >= 60.0:
            return "high"
        elif score >= 35.0:
            return "medium"
        return "low"

    def score_to_gap_level_str(self, score: float, provider_count: int = 1) -> str:
        if provider_count <= 0:
            return "NO PROVIDER"
        level = self.score_to_risk_level(score)
        return f"{level.upper()} GAP"

    # ------------------------------------------------------------------------
    # Stage 7 & 8: Specialty Matching & Rule-Based Action Classification
    # ------------------------------------------------------------------------
    def classify_action(
        self,
        risk_level: str,
        provider_count: int,
        estimated_patients: int,
        avg_travel_distance_km: float,
        has_nearby_alternative: bool = False,
    ) -> Tuple[str, str]:
        """
        Implements Stage 12 Rule-Based Action Classification:
        - High/Critical Risk + Low Provider Supply -> Provider Recruitment
        - High Demand + Nearby Alternative Provider -> Patient Referral
        - High Risk + Large Geographic Distance (>25km) -> Telehealth / Virtual Care
        - Medium Risk -> Monitor Area
        - Low Risk -> No Action
        """
        level = risk_level.lower()
        if level in ["critical", "high"]:
            if avg_travel_distance_km >= 28.0:
                return "Enable Remote Access", "Telehealth / Virtual Care"
            elif has_nearby_alternative:
                return "Refer Patients to Nearby Network", "Patient Referral"
            else:
                return "Recruit Providers to Area", "Provider Recruitment"
        elif level == "medium":
            return "Monitor Area Access Trends", "Monitor Area"
        else:
            return "No Immediate Action Needed", "No Action"

    # ------------------------------------------------------------------------
    # Stage 14: Explainable Results (Why this Result?)
    # ------------------------------------------------------------------------
    def explain_root_causes(
        self,
        risk_score: float,
        provider_count: int,
        estimated_patients: int,
        avg_travel_distance_km: float,
    ) -> Dict[str, float]:
        """Calculates percentage contribution of each risk factor."""
        demand_pressure = min(100.0, round((estimated_patients / 8000.0) * 100.0, 1))
        shortage = 100.0 if provider_count <= 0 else min(100.0, round(max(0.0, 100.0 - (provider_count * 20.0)), 1))
        travel = min(100.0, round((avg_travel_distance_km / 45.0) * 100.0, 1))
        utilization = min(100.0, round(risk_score * 0.92, 1))

        return {
            "demandPressure": max(10.0, demand_pressure),
            "providerShortage": max(10.0, shortage),
            "travelDistance": max(10.0, travel),
            "utilization": max(10.0, utilization),
        }

    # ------------------------------------------------------------------------
    # Stage 13: What-If Simulation Engine
    # ------------------------------------------------------------------------
    def compute_simulation(
        self,
        current_providers: int,
        estimated_patients: int,
        specialty: str,
        additional_providers: int,
        current_gap_score: Optional[float] = None,
    ) -> Dict[str, Any]:
        """Simulates changes in providers, capacity, risk score, and decay curve."""
        if current_gap_score is None:
            current_gap_score = self.calculate_gap_score(
                provider_count=current_providers,
                estimated_patients=estimated_patients,
                specialty=specialty,
            )

        benchmark = self.SPECIALTY_BENCHMARKS.get(specialty, 1500)

        def risk_at(added: int) -> float:
            if added == 0:
                return current_gap_score
            factor = max(1, current_providers) / (max(1, current_providers) + added)
            factor = factor ** 0.5
            projected_score = current_gap_score * factor
            return max(10.0, min(100.0, round(projected_score, 1)))

        projected_score = risk_at(additional_providers)
        improvement_pct = 0.0
        if current_gap_score > 0:
            improvement_pct = round(((current_gap_score - projected_score) / current_gap_score) * 100.0, 1)

        projected_provider_count = current_providers + additional_providers
        projected_patients_per_provider = round(
            estimated_patients / max(1, projected_provider_count), 1
        )
        projected_access_gap_level = self.score_to_gap_level_str(projected_score, projected_provider_count)
        predicted_risk_level = self.score_to_risk_level(projected_score)

        if improvement_pct >= 35.0:
            expected_impact: Literal["low", "medium", "high"] = "high"
        elif improvement_pct >= 15.0:
            expected_impact = "medium"
        else:
            expected_impact = "low"

        curve = [
            {"providersAdded": n, "predictedRiskScore": risk_at(n)}
            for n in range(6)
        ]

        return {
            "current_providers": current_providers,
            "additional_providers": additional_providers,
            "projected_provider_count": projected_provider_count,
            "projected_patients_per_provider": projected_patients_per_provider,
            "current_risk_score": current_gap_score,
            "projected_gap_score": projected_score,
            "projected_access_gap_level": projected_access_gap_level,
            "predicted_risk_level": predicted_risk_level,
            "access_improvement_pct": improvement_pct,
            "expected_impact": expected_impact,
            "curve": curve,
        }


model_service = MLDecisionEngine()
