import os
import sys
import json
import logging
import csv
import numpy as np
import joblib
from sklearn.ensemble import GradientBoostingClassifier, IsolationForest
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score, precision_score, recall_score, f1_score, roc_auc_score, confusion_matrix

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("XGBoostEval")

MODELS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "models")
DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
os.makedirs(MODELS_DIR, exist_ok=True)

print("==========================================================")
print("  XGBOOST / GRADIENT BOOSTING MODEL EVALUATION (ACCURACY & RECALL)")
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

logger.info(f"Total dataset records: {len(rows)}")

# 2. Extract operational features (NO label leakage)
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

    # Feature vector
    feat = [patients, providers, patients_per_prov, benes, srvcs]
    X_list.append(feat)

    # Label: 1 = Access Gap / Shortage, 0 = Adequate Network
    is_gap = 1 if any(k in gap_level for k in ["CRITICAL", "HIGH", "NO PROVIDER"]) or gap_score >= 60.0 else 0
    y_list.append(is_gap)

X = np.array(X_list, dtype=np.float64)
y = np.array(y_list, dtype=np.int32)

# 3. Train-Test Split (80/20) & Standard Scaling
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)
X_train, X_test, y_train, y_test = train_test_split(X_scaled, y, test_size=0.20, random_state=42, stratify=y)

# 4. Train Gradient Boosting / XGBoost Classifier
xgb_model = GradientBoostingClassifier(
    n_estimators=100,
    learning_rate=0.08,
    max_depth=3,
    subsample=0.85,
    random_state=42
)
xgb_model.fit(X_train, y_train)

# 5. Evaluate Metrics
y_pred = xgb_model.predict(X_test)
y_prob = xgb_model.predict_proba(X_test)[:, 1]

acc = accuracy_score(y_test, y_pred)
prec = precision_score(y_test, y_pred)
rec = recall_score(y_test, y_pred)
f1 = f1_score(y_test, y_pred)
auc = roc_auc_score(y_test, y_prob)
cm = confusion_matrix(y_test, y_pred)

print("\n----------------------------------------------------------")
print("  XGBOOST CLASSIFIER EVALUATION METRICS")
print("----------------------------------------------------------")
print(f"  • Accuracy:        {acc * 100.0:.2f}%")
print(f"  • Precision:       {prec * 100.0:.2f}%")
print(f"  • Recall:          {rec * 100.0:.2f}%  <-- (Crucial for Healthcare Gap Detection)")
print(f"  • F1-Score:        {f1 * 100.0:.2f}%")
print(f"  • ROC-AUC Score:   {auc:.3f}")
print("\nConfusion Matrix:")
print(f"  TN={cm[0][0]}  FP={cm[0][1]}")
print(f"  FN={cm[1][0]}  TP={cm[1][1]}")

print("\nDetailed Classification Report:")
print(classification_report(y_test, y_pred, target_names=["Adequate Network (0)", "Access Shortage (1)"]))

# 6. Train K-Means & Isolation Forest
kmeans_model = KMeans(n_clusters=4, random_state=42, n_init=10)
cluster_labels = kmeans_model.fit_predict(X_scaled)

isolation_forest = IsolationForest(contamination=0.08, random_state=42)
isolation_forest.fit(X_scaled)
anomalies_count = np.sum(isolation_forest.predict(X_scaled) == -1)

# 7. Save Model Artifacts
classifier_path = os.path.join(MODELS_DIR, "xgboost_gap_classifier.pkl")
kmeans_path = os.path.join(MODELS_DIR, "kmeans_cluster_model.pkl")
isolation_path = os.path.join(MODELS_DIR, "isolation_forest_anomaly.pkl")
scaler_path = os.path.join(MODELS_DIR, "scaler.pkl")
meta_path = os.path.join(MODELS_DIR, "model_metadata.json")

joblib.dump(xgb_model, classifier_path)
joblib.dump(kmeans_model, kmeans_path)
joblib.dump(isolation_forest, isolation_path)
joblib.dump(scaler, scaler_path)

metadata = {
    "model_type": "XGBoost / Gradient Boosting Classifier",
    "trained_at_records": len(rows),
    "features": [
        "estimated_patients",
        "provider_count",
        "patients_per_provider",
        "total_beneficiaries",
        "total_services",
    ],
    "accuracy_pct": round(float(acc) * 100.0, 2),
    "precision_pct": round(float(prec) * 100.0, 2),
    "recall_pct": round(float(rec) * 100.0, 2),
    "f1_score_pct": round(float(f1) * 100.0, 2),
    "roc_auc_score": round(float(auc), 3),
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

# Also update train_models.py so python train_models.py runs this exact pipeline
with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "train_models.py"), "w") as f_tr:
    with open(__file__, "r") as f_self:
        f_tr.write(f_self.read())

print("==========================================================")
print("  MODEL ARTIFACTS SAVED SUCCESSFULLY TO backend/models/")
print("==========================================================\n")
