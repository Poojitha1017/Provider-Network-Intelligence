import os
import shutil
import zipfile
import pandas as pd

# Source raw datasets directory
raw_dir = r"C:\Users\HP\Downloads\UC05_ALL_FOUR_DATASETS_UPDATED"
output_dir = r"C:\Users\HP\Downloads\UC05_Cleaned_Datasets_Database_Schema"
os.makedirs(output_dir, exist_ok=True)

backend_data_dir = r"C:\Users\HP\Downloads\frontend\backend\data"
os.makedirs(backend_data_dir, exist_ok=True)

print("Processing and cleaning raw UC05 datasets based on database schema...")

# 1. Process Decision Dataset (2,000 rows)
decision_path = os.path.join(raw_dir, "UC05_DECISION_FINAL_WITH_DISEASE.csv")
if os.path.exists(decision_path):
    df_dec = pd.read_csv(decision_path)
    
    # Rename COUNTY_NAME to CITY if CITY is missing
    if "CITY" not in df_dec.columns and "COUNTY_NAME" in df_dec.columns:
        df_dec["CITY"] = df_dec["COUNTY_NAME"].astype(str).str.replace(" County", "", regex=False).str.upper()
    
    # Fill any null values
    df_dec["ESTIMATED_PATIENTS"] = df_dec["ESTIMATED_PATIENTS"].fillna(1000).astype(int)
    df_dec["PROVIDER_COUNT"] = df_dec["PROVIDER_COUNT"].fillna(1).astype(int)
    df_dec["TOTAL_BENEFICIARIES"] = df_dec["TOTAL_BENEFICIARIES"].fillna(df_dec["ESTIMATED_PATIENTS"] * 3).astype(int)
    df_dec["TOTAL_SERVICES"] = df_dec["TOTAL_SERVICES"].fillna(df_dec["ESTIMATED_PATIENTS"] * 8).astype(float)
    df_dec["PATIENTS_PER_PROVIDER"] = df_dec["PATIENTS_PER_PROVIDER"].fillna(df_dec["ESTIMATED_PATIENTS"] / df_dec["PROVIDER_COUNT"]).round(1)
    df_dec["MEDIAN_PATIENTS_PER_PROVIDER"] = df_dec["MEDIAN_PATIENTS_PER_PROVIDER"].fillna(1200.0).round(1)
    df_dec["MEAN_PATIENTS_PER_PROVIDER"] = df_dec["MEAN_PATIENTS_PER_PROVIDER"].fillna(1350.0).round(1)
    df_dec["GAP_RATIO"] = df_dec["GAP_RATIO"].fillna((df_dec["GAP_SCORE"] / 40.0).round(2))
    df_dec["ACCESS_GAP_LEVEL"] = df_dec["ACCESS_GAP_LEVEL"].fillna("MODERATE GAP")
    df_dec["GAP_SCORE"] = df_dec["GAP_SCORE"].fillna(50.0).round(1)
    df_dec["UC05_KEY"] = df_dec["COUNTY_FIPS"].astype(str) + "_" + df_dec["REQUIRED_SPECIALTY"].astype(str)

    target_cols_dec = [
        "COUNTY_FIPS", "STATEDESC", "CITY", "REQUIRED_SPECIALTY", "DISEASE",
        "ESTIMATED_PATIENTS", "PROVIDER_COUNT", "TOTAL_BENEFICIARIES", "TOTAL_SERVICES",
        "PATIENTS_PER_PROVIDER", "MEDIAN_PATIENTS_PER_PROVIDER", "MEAN_PATIENTS_PER_PROVIDER",
        "GAP_RATIO", "ACCESS_GAP_LEVEL", "GAP_SCORE", "UC05_KEY"
    ]
    df_dec_cleaned = df_dec[[c for c in target_cols_dec if c in df_dec.columns]]
    out_dec_path = os.path.join(output_dir, "UC05_DECISION_CLEANED.csv")
    df_dec_cleaned.to_csv(out_dec_path, index=False)
    df_dec_cleaned.to_csv(os.path.join(backend_data_dir, "UC05_DECISION_CLEANED.csv"), index=False)
    print(f"  [1/5] Decision Dataset Cleaned: {df_dec_cleaned.shape[0]} rows, {df_dec_cleaned.shape[1]} columns -> {out_dec_path}")

# 2. Process Providers Dataset (55 rows)
providers_path = os.path.join(raw_dir, "UC05_PROVIDER_FINAL_WITH_DISEASE.csv")
if os.path.exists(providers_path):
    df_prov = pd.read_csv(providers_path)
    df_prov["COUNTY_FIPS"] = df_prov["COUNTY_FIPS"].astype(str).str.zfill(5)
    df_prov["STATE"] = df_prov["STATE"].astype(str).str.upper()
    df_prov["TOT_BENES"] = df_prov["TOT_BENES"].fillna(500).astype(int)
    df_prov["TOT_SRVCS"] = df_prov["TOT_SRVCS"].fillna(1500.0).astype(float)
    df_prov["BENE_AVG_RISK_SCRE"] = df_prov["BENE_AVG_RISK_SCRE"].fillna(1.5).round(2)
    df_prov["TOTAL_UTILIZATION_EXACT"] = df_prov["TOTAL_UTILIZATION_EXACT"].fillna(75.0).round(1)
    df_prov["AVG_UTILIZATION_PERCENTILE"] = df_prov["AVG_UTILIZATION_PERCENTILE"].fillna(60.0).round(1)

    target_cols_prov = [
        "NPI", "PROVIDER_NAME", "PRIMARY_SPECIALTY", "DISEASE", "SECONDARY_SPECIALTY",
        "TELEHEALTH", "FACILITY_NAME", "CITY", "STATE", "ZIP", "COUNTY_FIPS", "COUNTY",
        "TOT_BENES", "TOT_SRVCS", "BENE_AVG_RISK_SCRE", "TOTAL_UTILIZATION_EXACT", "AVG_UTILIZATION_PERCENTILE"
    ]
    df_prov_cleaned = df_prov[[c for c in target_cols_prov if c in df_prov.columns]]
    out_prov_path = os.path.join(output_dir, "UC05_PROVIDERS_CLEANED.csv")
    df_prov_cleaned.to_csv(out_prov_path, index=False)
    df_prov_cleaned.to_csv(os.path.join(backend_data_dir, "UC05_PROVIDERS_CLEANED.csv"), index=False)
    print(f"  [2/5] Providers Dataset Cleaned: {df_prov_cleaned.shape[0]} rows, {df_prov_cleaned.shape[1]} columns -> {out_prov_path}")

# 3. Process Supply Dataset (50 rows)
supply_path = os.path.join(raw_dir, "UC05_SUPPLY_FINAL_WITH_DISEASE.csv")
if os.path.exists(supply_path):
    df_sup = pd.read_csv(supply_path)
    df_sup["COUNTY_FIPS"] = df_sup["COUNTY_FIPS"].astype(str).str.zfill(5)
    df_sup["STATE"] = df_sup["STATE"].astype(str).str.upper()
    df_sup["PROVIDER_COUNT"] = df_sup["PROVIDER_COUNT"].fillna(1).astype(int)
    df_sup["TOTAL_BENEFICIARIES"] = df_sup["TOTAL_BENEFICIARIES"].fillna(1000).astype(int)
    df_sup["TOTAL_SERVICES"] = df_sup["TOTAL_SERVICES"].fillna(3000.0).astype(float)

    out_sup_path = os.path.join(output_dir, "UC05_SUPPLY_CLEANED.csv")
    df_sup.to_csv(out_sup_path, index=False)
    df_sup.to_csv(os.path.join(backend_data_dir, "UC05_SUPPLY_CLEANED.csv"), index=False)
    print(f"  [3/5] Supply Dataset Cleaned: {df_sup.shape[0]} rows, {df_sup.shape[1]} columns -> {out_sup_path}")

# 4. Process Service Area Dataset (26 rows)
sa_path = os.path.join(raw_dir, "UC05_SERVICE_AREA_FINAL.csv")
if os.path.exists(sa_path):
    df_sa = pd.read_csv(sa_path)
    out_sa_path = os.path.join(output_dir, "UC05_SERVICE_AREAS_CLEANED.csv")
    df_sa.to_csv(out_sa_path, index=False)
    df_sa.to_csv(os.path.join(backend_data_dir, "UC05_SERVICE_AREAS_CLEANED.csv"), index=False)
    print(f"  [4/5] Service Area Dataset Cleaned: {df_sa.shape[0]} rows, {df_sa.shape[1]} columns -> {out_sa_path}")

# 5. Build Filter Options Dataset
if os.path.exists(out_dec_path):
    df_filter = df_dec_cleaned[["STATEDESC", "CITY", "COUNTY_FIPS", "REQUIRED_SPECIALTY", "DISEASE", "ACCESS_GAP_LEVEL"]].drop_duplicates()
    df_filter.columns = ["state", "city", "county_fips", "specialty", "disease", "risk_level"]
    out_filter_path = os.path.join(output_dir, "UC05_FILTER_OPTIONS_CLEANED.csv")
    df_filter.to_csv(out_filter_path, index=False)
    df_filter.to_csv(os.path.join(backend_data_dir, "UC05_FILTER_OPTIONS_CLEANED.csv"), index=False)
    print(f"  [5/5] Filter Options Dataset Generated: {df_filter.shape[0]} rows -> {out_filter_path}")

# Create ZIP archive in Downloads and in backend/data/
zip_path_downloads = r"C:\Users\HP\Downloads\UC05_Cleaned_Datasets_Database_Schema.zip"
zip_path_backend = os.path.join(backend_data_dir, "UC05_Cleaned_Datasets_Database_Schema.zip")

with zipfile.ZipFile(zip_path_downloads, "w", zipfile.ZIP_DEFLATED) as zipf:
    for root, dirs, files in os.walk(output_dir):
        for file in files:
            full_path = os.path.join(root, file)
            rel_path = os.path.relpath(full_path, output_dir)
            zipf.write(full_path, arcname=rel_path)

shutil.copyfile(zip_path_downloads, zip_path_backend)

print(f"\n[SUCCESS] All cleaned datasets generated and zipped successfully!")
print(f"  Folder: {output_dir}")
print(f"  ZIP File: {zip_path_downloads}")
print(f"  Backend Copy: {zip_path_backend}")
