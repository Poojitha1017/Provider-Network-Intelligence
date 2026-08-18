import os
import sys
from dotenv import load_dotenv
from supabase import create_client

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
load_dotenv()

from app.services.decision_service import RAW_SEED_DATA, SPECIALTY_TO_DISEASE_MAP, STATE_CODE_MAP

url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_SERVICE_ROLE_KEY") or os.getenv("SUPABASE_ANON_KEY")

print("==================================================")
print("SEEDING PROVIDERS & COUNTY RECORDS INTO SUPABASE")
print("==================================================")
print(f"Connecting to Supabase: {url}")

if not url or not key:
    print("[ERROR] Missing Supabase credentials.")
    sys.exit(1)

client = create_client(url, key)

provider_rows = []
for idx, seed in enumerate(RAW_SEED_DATA):
    fips = seed["county_fips"]
    state_code = STATE_CODE_MAP.get(seed["state"], "TX")
    spec = seed["specialty"]
    disease = SPECIALTY_TO_DISEASE_MAP.get(spec, "Chronic Care")
    risk = float(seed["risk"])
    supply = int(seed["supply"])
    pop = int(seed["pop"])
    access_level = "CRITICAL GAP" if risk >= 85 else ("HIGH GAP" if risk >= 65 else ("MODERATE GAP" if risk >= 40 else "ADEQUATE"))

    npi = f"990000{idx + 1:04d}"
    name = f"DR. {seed['city']} SPECIALIST"
    
    row = {
        "NPI": npi,
        "PROVIDER_NAME": name,
        "PRIMARY_SPECIALTY": spec,
        "STATE": state_code,
        "ZIP": f"{int(fips) * 10 if len(fips) == 5 else 75000}",
        "COUNTY_FIPS": fips,
        "COUNTY": f"{seed['city']} County",
        "FACILITY_NAME": f"{seed['city']} Medical Center",
        "TELEHEALTH": "Yes" if supply <= 2 else "No",
        "TELEHEALTH_FLAG": "1" if supply <= 2 else "0",
        "TOT_BENES": pop,
        "TOT_SRVCS": pop * 3,
        "BENE_AVG_RISK_SCRE": round(risk / 35.0, 2),
        "TOTAL_UTILIZATION_EXACT": round(risk * 0.9, 1),
        "AVG_UTILIZATION_PERCENTILE": round(risk, 1),
        "DISEASE": disease,
        "AREA_PROVIDER_COUNT": supply,
        "AREA_TOTAL_BENEFICIARIES": pop * 3,
        "AREA_TOTAL_SERVICES": pop * 8,
        "BENEFICIARIES_PER_PROVIDER": round(pop / max(1, supply), 1),
        "REQUIRED_PROVIDERS": max(1, round(risk / 25.0)),
        "PROVIDER_SHORTAGE": max(0, 5 - supply),
        "AREA_RISK_SCORE": risk,
        "RISK_SCORE": risk,
        "ACCESS_LEVEL": access_level,
        "RECOMMENDED_ADDITIONAL_PROVIDERS": max(0, 5 - supply)
    }
    provider_rows.append(row)

print(f"Total provider/county records prepared for insertion: {len(provider_rows)}")

try:
    # Insert batch
    batch_size = 20
    inserted = 0
    for i in range(0, len(provider_rows), batch_size):
        batch = provider_rows[i:i + batch_size]
        res = client.table("providers").upsert(batch, on_conflict="NPI").execute()
        count = len(res.data) if res.data else 0
        inserted += count
        print(f"  Upserted batch {i // batch_size + 1}: {count} records")

    print(f"\n[SUCCESS] Successfully seeded {inserted} provider & county records into Supabase 'providers' table!")

    # Verify total count
    check_res = client.table("providers").select("NPI", count="exact").limit(1).execute()
    print(f"[VERIFIED] Live 'providers' table total record count: {check_res.count}")

except Exception as e:
    print(f"\n[ERROR] Seeding failed: {e}")

print("==================================================")
