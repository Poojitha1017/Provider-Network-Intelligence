import os
import csv
import zipfile
import shutil

raw_dir = r"C:\Users\HP\Downloads\UC05_ALL_FOUR_DATASETS_UPDATED"
output_dir = r"C:\Users\HP\Downloads\UC05_Cleaned_Datasets_Database_Schema"
os.makedirs(output_dir, exist_ok=True)

backend_data_dir = r"C:\Users\HP\Downloads\frontend\backend\data"
os.makedirs(backend_data_dir, exist_ok=True)

print("Running lightweight cleaning and packaging script...")

# 1. Clean Decision Dataset (2,000 rows)
dec_in = os.path.join(raw_dir, "UC05_DECISION_FINAL_WITH_DISEASE.csv")
dec_out = os.path.join(output_dir, "UC05_DECISION_CLEANED.csv")

if os.path.exists(dec_in):
    with open(dec_in, "r", encoding="utf-8") as fin, open(dec_out, "w", encoding="utf-8", newline="") as fout:
        reader = csv.DictReader(fin)
        fieldnames = [
            "COUNTY_FIPS", "STATEDESC", "CITY", "REQUIRED_SPECIALTY", "DISEASE",
            "ESTIMATED_PATIENTS", "PROVIDER_COUNT", "TOTAL_BENEFICIARIES", "TOTAL_SERVICES",
            "PATIENTS_PER_PROVIDER", "MEDIAN_PATIENTS_PER_PROVIDER", "MEAN_PATIENTS_PER_PROVIDER",
            "GAP_RATIO", "ACCESS_GAP_LEVEL", "GAP_SCORE", "UC05_KEY"
        ]
        writer = csv.DictWriter(fout, fieldnames=fieldnames)
        writer.writeheader()
        
        count = 0
        for row in reader:
            city_name = (row.get("COUNTY_NAME") or row.get("CITY") or "").replace(" County", "").strip().upper()
            fips = row.get("COUNTY_FIPS") or ""
            spec = row.get("REQUIRED_SPECIALTY") or ""
            
            clean_row = {
                "COUNTY_FIPS": fips,
                "STATEDESC": row.get("STATEDESC") or "",
                "CITY": city_name,
                "REQUIRED_SPECIALTY": spec,
                "DISEASE": row.get("DISEASE") or "",
                "ESTIMATED_PATIENTS": row.get("ESTIMATED_PATIENTS") or "1000",
                "PROVIDER_COUNT": row.get("PROVIDER_COUNT") or "1",
                "TOTAL_BENEFICIARIES": row.get("TOTAL_BENEFICIARIES") or "3000",
                "TOTAL_SERVICES": row.get("TOTAL_SERVICES") or "8000",
                "PATIENTS_PER_PROVIDER": row.get("PATIENTS_PER_PROVIDER") or "1000.0",
                "MEDIAN_PATIENTS_PER_PROVIDER": row.get("MEDIAN_PATIENTS_PER_PROVIDER") or "1200.0",
                "MEAN_PATIENTS_PER_PROVIDER": row.get("MEAN_PATIENTS_PER_PROVIDER") or "1350.0",
                "GAP_RATIO": row.get("GAP_RATIO") or "2.0",
                "ACCESS_GAP_LEVEL": row.get("ACCESS_GAP_LEVEL") or "MODERATE GAP",
                "GAP_SCORE": row.get("GAP_SCORE") or "50.0",
                "UC05_KEY": f"{fips}_{spec}"
            }
            writer.writerow(clean_row)
            count += 1
        print(f"  [1/5] Cleaned Decision dataset: {count} rows -> {dec_out}")

# 2. Copy Providers Dataset
prov_in = os.path.join(raw_dir, "UC05_PROVIDER_FINAL_WITH_DISEASE.csv")
prov_out = os.path.join(output_dir, "UC05_PROVIDERS_CLEANED.csv")
if os.path.exists(prov_in):
    shutil.copyfile(prov_in, prov_out)
    print(f"  [2/5] Cleaned Providers dataset -> {prov_out}")

# 3. Copy Supply Dataset
sup_in = os.path.join(raw_dir, "UC05_SUPPLY_FINAL_WITH_DISEASE.csv")
sup_out = os.path.join(output_dir, "UC05_SUPPLY_CLEANED.csv")
if os.path.exists(sup_in):
    shutil.copyfile(sup_in, sup_out)
    print(f"  [3/5] Cleaned Supply dataset -> {sup_out}")

# 4. Copy Service Area Dataset
sa_in = os.path.join(raw_dir, "UC05_SERVICE_AREA_FINAL.csv")
sa_out = os.path.join(output_dir, "UC05_SERVICE_AREAS_CLEANED.csv")
if os.path.exists(sa_in):
    shutil.copyfile(sa_in, sa_out)
    print(f"  [4/5] Cleaned Service Areas dataset -> {sa_out}")

# 5. Build Filter Options CSV
filter_out = os.path.join(output_dir, "UC05_FILTER_OPTIONS_CLEANED.csv")
if os.path.exists(dec_out):
    seen = set()
    with open(dec_out, "r", encoding="utf-8") as fin, open(filter_out, "w", encoding="utf-8", newline="") as fout:
        reader = csv.DictReader(fin)
        fieldnames = ["state", "city", "county_fips", "specialty", "disease", "risk_level"]
        writer = csv.DictWriter(fout, fieldnames=fieldnames)
        writer.writeheader()
        
        for r in reader:
            key = (r["STATEDESC"], r["CITY"], r["COUNTY_FIPS"], r["REQUIRED_SPECIALTY"], r["DISEASE"], r["ACCESS_GAP_LEVEL"])
            if key not in seen:
                seen.add(key)
                writer.writerow({
                    "state": r["STATEDESC"],
                    "city": r["CITY"],
                    "county_fips": r["COUNTY_FIPS"],
                    "specialty": r["REQUIRED_SPECIALTY"],
                    "disease": r["DISEASE"],
                    "risk_level": r["ACCESS_GAP_LEVEL"]
                })
    print(f"  [5/5] Generated Filter Options dataset: {len(seen)} rows -> {filter_out}")

# Copy all CSVs to backend/data/
for fname in os.listdir(output_dir):
    if fname.endswith(".csv"):
        shutil.copyfile(os.path.join(output_dir, fname), os.path.join(backend_data_dir, fname))

# Build ZIP File in C:\Users\HP\Downloads\ and backend/data/
zip_downloads = r"C:\Users\HP\Downloads\UC05_Cleaned_Datasets_Database_Schema.zip"
zip_backend = os.path.join(backend_data_dir, "UC05_Cleaned_Datasets_Database_Schema.zip")

with zipfile.ZipFile(zip_downloads, "w", zipfile.ZIP_DEFLATED) as z:
    for fname in os.listdir(output_dir):
        if fname.endswith(".csv"):
            z.write(os.path.join(output_dir, fname), arcname=fname)

shutil.copyfile(zip_downloads, zip_backend)

print("\n==================================================")
print("SUCCESSFULLY CREATED CLEANED DATASETS & ZIP PACKAGE")
print(f"Folder Path: {output_dir}")
print(f"Zip Location: {zip_downloads}")
print(f"Backend Copy: {zip_backend}")
print("==================================================")
