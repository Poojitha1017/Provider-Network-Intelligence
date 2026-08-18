import os
import sys
import json
from dotenv import load_dotenv

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
load_dotenv()

from supabase import create_client
from app.services.decision_service import FALLBACK_DECISIONS

url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_SERVICE_ROLE_KEY") or os.getenv("SUPABASE_ANON_KEY")

print("==================================================")
print("SEEDING DATASET INTO SUPABASE DATABASE")
print("==================================================")
print(f"Connecting to Supabase: {url}")

if not url or not key:
    print("[ERROR] Missing Supabase credentials.")
    sys.exit(1)

client = create_client(url, key)

print(f"Total decision records to insert: {len(FALLBACK_DECISIONS)}")

insert_rows = []
for r in FALLBACK_DECISIONS:
    row = {
        "COUNTY_FIPS": r["COUNTY_FIPS"],
        "STATEDESC": r["STATEDESC"],
        "REQUIRED_SPECIALTY": r["REQUIRED_SPECIALTY"],
        "ESTIMATED_PATIENTS": r["ESTIMATED_PATIENTS"],
        "PROVIDER_COUNT": r["PROVIDER_COUNT"],
        "TOTAL_BENEFICIARIES": r["TOTAL_BENEFICIARIES"],
        "TOTAL_SERVICES": r["TOTAL_SERVICES"],
        "PATIENTS_PER_PROVIDER": r["PATIENTS_PER_PROVIDER"],
        "MEDIAN_PATIENTS_PER_PROVIDER": r["MEDIAN_PATIENTS_PER_PROVIDER"],
        "MEAN_PATIENTS_PER_PROVIDER": r["MEAN_PATIENTS_PER_PROVIDER"],
        "GAP_RATIO": r["GAP_RATIO"],
        "ACCESS_GAP_LEVEL": r["ACCESS_GAP_LEVEL"],
        "GAP_SCORE": r["GAP_SCORE"],
        "UC05_KEY": r["UC05_KEY"],
        "DISEASE": r["DISEASE"],
    }
    insert_rows.append(row)

print("Attempting insertion into table 'decision'...")
try:
    batch_size = 20
    inserted_count = 0
    for i in range(0, len(insert_rows), batch_size):
        batch = insert_rows[i:i + batch_size]
        res = client.table("decision").insert(batch).execute()
        count = len(res.data) if res.data else 0
        inserted_count += count
        print(f"  Inserted batch {i // batch_size + 1}: {count} records")

    print(f"\n[SUCCESS] Successfully inserted {inserted_count} records into 'decision' table!")

    # Verify count in Supabase
    check_res = client.table("decision").select("*", count="exact").execute()
    print(f"[VERIFIED] Live 'decision' table record count: {check_res.count}")
    if check_res.data:
        print("Sample inserted row columns:", list(check_res.data[0].keys()))

except Exception as e:
    print(f"\n[ERROR] Insertion failed: {e}")

print("==================================================")
