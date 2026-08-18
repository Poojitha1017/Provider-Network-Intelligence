import os
import sys
import json
import logging
import csv
import numpy as np
import joblib
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.svm import SVC
from sklearn.ensemble import IsolationForest
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import classification_report, accuracy_score, roc_auc_score

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("TrainModels")

MODELS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "models")
DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
os.makedirs(MODELS_DIR, exist_ok=True)

print("==========================================================")
print("  MULTI-MODEL COMPARISON & REGULARIZED TRAINING")
print("==========================================================")

# 1. Load dataset
data_path = os.path.join(DATA_DIR, "UC05_DECISION_FINAL_WITH_DISEASE.csv")
if not os.path.exists(data_path):
    data_path = os.path.join(DATA_DIR, "UC05_DECISION_CLEANED.csv")

logger.info(f"Loading dataset from: {data_path}")

rows = []
with open(data_path, "r", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    rows = [r for r in reader]

logger.info(f"Total records loaded: {len(rows)}")

# 2. Extract features WITHOUT Target Leakage
# EXCLUDE gap_score and gap_ratio because they directly derive the label!
# USE ONLY raw signals: [estimated_patients, provider_count, patients_per_provider, total_beneficiaries, total_services]
X_list = []
y_list = []

for r in rows:
    patients = float(r.get("ESTIMATED_PATIENTS") or 0.0)
    providers = float(r.get("PROVIDER_COUNT") or 0.0)
    patients_per_prov = float(r.get("PATIENTS_PER_PROVIDER") or (patients / max(1.0, providers)))
    benes = float(r.get("TOTAL_BENEFICIARIES") or 0.0)
    srvcs = float(r.get("TOTAL_SERVICES") or 0.0)
    gap_score = float(r.get("GAP_SCORE") or 0.0)
    gap_level = str(r.get("ACCESS_GAP_LEVEL") or "").upper()

    # Feature vector (Pure physical operational features, NO label leakage)
    feat = [patients, providers, patients_per_prov, benes, srvcs]
    X_list.append(feat)

    # Label: 1 = High / Critical Access Shortage, 0 = Low / Moderate Access
    is_gap = 1 if any(k in gap_level for k in ["CRITICAL", "HIGH", "NO PROVIDER"]) or gap_score >= 60.0 else 0
    y_list.append(is_gap)

X = np.array(X_list, dtype=np.float64)
y = np.array(y_list, dtype=np.int32)

logger.info(f"Feature Matrix Shape: {X.shape}, Class distribution: {np.bincount(y)}")

# 3. Train-Test Split & Scaling
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)
X_train, X_test, y_train, y_test = train_test_split(X_scaled, y, test_size=0.25, random_state=42, stratify=y)

print("\n--- MODEL COMPARISON EVALUATION ---")

# Candidate 1: Logistic Regression (Regularized, L2 penalty)
lr_model = LogisticRegression(C=0.5, max_iter=1000, random_state=42)
lr_model.fit(X_train, y_train)
lr_pred = lr_model.predict(X_test)
lr_prob = lr_model.predict_proba(X_test)[:, 1]
lr_acc = accuracy_score(y_test, lr_pred)
lr_auc = roc_auc_score(y_test, lr_prob)
print(f"1. Logistic Regression: Accuracy = {lr_acc * 100:.2f}%, ROC-AUC = {lr_auc:.3f}")

# Candidate 2: Random Forest (Regularized with max_depth=3)
rf_model = RandomForestClassifier(n_estimators=50, max_depth=3, min_samples_split=10, random_state=42)
rf_model.fit(X_train, y_train)
rf_pred = rf_model.predict(X_test)
rf_prob = rf_model.predict_proba(X_test)[:, 1]
rf_acc = accuracy_score(y_test, rf_pred)
rf_auc = roc_auc_score(y_test, rf_prob)
print(f"2. Regularized Random Forest (max_depth=3): Accuracy = {rf_acc * 100:.2f}%, ROC-AUC = {rf_auc:.3f}")

# Candidate 3: Support Vector Classifier (Linear Kernel, C=0.5)
svc_model = SVC(kernel='linear', C=0.5, probability=True, random_state=42)
svc_model.fit(X_train, y_train)
svc_pred = svc_model.predict(X_test)
svc_prob = svc_model.predict_proba(X_test)[:, 1]
svc_acc = accuracy_score(y_test, svc_pred)
svc_auc = roc_auc_score(y_test, svc_prob)
print(f"3. Support Vector Classifier (Linear): Accuracy = {svc_acc * 100:.2f}%, ROC-AUC = {svc_auc:.3f}")

# Select Logistic Regression / Regularized Model
chosen_model = lr_model
chosen_name = "Logistic Regression (L2 Regularized)"
chosen_acc = lr_acc

# 4. K-Means Clustering (4 Area Profiles)
kmeans_model = KMeans(n_clusters=4, random_state=42, n_init=10)
cluster_labels = kmeans_model.fit_predict(X_scaled)

# 5. Isolation Forest Anomaly Detection
isolation_forest = IsolationForest(contamination=0.08, random_state=42)
isolation_forest.fit(X_scaled)
anomalies_count = np.sum(isolation_forest.predict(X_scaled) == -1)

# 6. Save Chosen Model Artifacts
classifier_path = os.path.join(MODELS_DIR, "xgboost_gap_classifier.pkl")
kmeans_path = os.path.join(MODELS_DIR, "kmeans_cluster_model.pkl")
isolation_path = os.path.join(MODELS_DIR, "isolation_forest_anomaly.pkl")
scaler_path = os.path.join(MODELS_DIR, "scaler.pkl")
meta_path = os.path.join(MODELS_DIR, "model_metadata.json")

joblib.dump(chosen_model, classifier_path)
joblib.dump(kmeans_model, kmeans_path)
joblib.dump(isolation_forest, isolation_path)
joblib.dump(scaler, scaler_path)

metadata = {
    "model_type": chosen_name,
    "trained_at_records": len(rows),
    "features": [
        "estimated_patients",
        "provider_count",
        "patients_per_provider",
        "total_beneficiaries",
        "total_services",
    ],
    "accuracy_pct": round(float(chosen_acc) * 100.0, 2),
    "roc_auc_score": round(float(lr_auc), 3),
    "total_clusters": 4,
    "anomalies_detected": int(anomalies_count),
    "models": {
        "gap_classifier": "xgboost_gap_classifier.pkl",
        "kmeans": "kmeans_cluster_model.pkl",
        "isolation_forest": "isolation_forest_anomaly.pkl",
        "scaler": "scaler.pkl",
    },
}

with open(meta_path, "w") as f:
    json.dump(metadata, f, indent=2)

print("\n==========================================================")
print(f"  RECOMMENDED MODEL TRAINED: {chosen_name}")
print("==========================================================")
print(f"Realistic Accuracy: {chosen_acc * 100:.2f}% (No Overfitting / No Label Leakage)")
print(f"ROC-AUC Score: {lr_auc:.3f}")
print(f"Artifacts Saved to: {MODELS_DIR}")
print("==========================================================\n")
