import os
import sys
import json
from dotenv import load_dotenv

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
load_dotenv()

from supabase import create_client

url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_SERVICE_ROLE_KEY") or os.getenv("SUPABASE_ANON_KEY")

print("==================================================")
print("SUPABASE LIVE DIAGNOSTIC & DATA FLOW INSPECTION")
print("==================================================")
print(f"Connecting to Supabase at: {url}")

try:
    client = create_client(url, key)
    print("[SUCCESS] Connected to Supabase client successfully.\n")
except Exception as e:
    print(f"[ERROR] Failed to initialize Supabase client: {e}")
    sys.exit(1)

tables_to_check = [
    "providers",
    "provider_service_areas",
    "supply",
    "decision",
    "uc05_filter_options",
    "profiles",
]

table_info = {}

for table_name in tables_to_check:
    print(f"--- Checking Table: '{table_name}' ---")
    try:
        res = client.table(table_name).select("*", count="exact").limit(3).execute()
        count = res.count if res.count is not None else len(res.data)
        rows = res.data or []
        print(f"  Status: FOUND")
        print(f"  Total Records: {count}")
        if rows:
            columns = list(rows[0].keys())
            print(f"  Columns ({len(columns)}): {columns}")
            print(f"  Sample Row 1: {json.dumps(rows[0], default=str)}")
            table_info[table_name] = {"count": count, "columns": columns, "sample": rows[0]}
        else:
            print("  Table is empty (0 rows returned)")
            table_info[table_name] = {"count": 0, "columns": [], "sample": None}
    except Exception as e:
        print(f"  Status: ERROR / NOT FOUND - {e}")
        table_info[table_name] = {"error": str(e)}
    print()

print("==================================================")
print("TESTING END-TO-END DATA FLOW QUERIES")
print("==================================================")

# 1. Test Filter Options Table
print("1. Testing public.uc05_filter_options queries...")
try:
    f_res = client.table("uc05_filter_options").select("*").limit(5).execute()
    print(f"   [PASS] Retrieved {len(f_res.data)} sample filter records:")
    for r in f_res.data[:3]:
        print(f"      - {r}")
except Exception as e:
    print(f"   [FAIL] Filter query error: {e}")

# 2. Test Decision Table
print("\n2. Testing public.decision queries...")
try:
    d_res = client.table("decision").select("*").limit(5).execute()
    print(f"   [PASS] Retrieved {len(d_res.data)} decision records:")
    for r in d_res.data[:3]:
        print(f"      - County: {r.get('COUNTY_FIPS') or r.get('county_fips')}, Specialty: {r.get('REQUIRED_SPECIALTY') or r.get('required_specialty')}, Score: {r.get('GAP_SCORE') or r.get('gap_score')}, Level: {r.get('ACCESS_GAP_LEVEL') or r.get('access_gap_level')}")
except Exception as e:
    print(f"   [FAIL] Decision query error: {e}")

# 3. Test Providers Table
print("\n3. Testing public.providers queries...")
try:
    p_res = client.table("providers").select("*").limit(5).execute()
    print(f"   [PASS] Retrieved {len(p_res.data)} provider records:")
    for r in p_res.data[:3]:
        print(f"      - NPI: {r.get('npi') or r.get('NPI')}, Name: {r.get('PROVIDER_NAME') or r.get('provider_name')}, Specialty: {r.get('PRIMARY_SPECIALTY') or r.get('primary_specialty')}, State: {r.get('STATE') or r.get('state')}")
except Exception as e:
    print(f"   [FAIL] Providers query error: {e}")

# 4. Test Supply Table
print("\n4. Testing public.supply queries...")
try:
    s_res = client.table("supply").select("*").limit(5).execute()
    print(f"   [PASS] Retrieved {len(s_res.data)} supply records:")
    for r in s_res.data[:3]:
        print(f"      - FIPS: {r.get('COUNTY_FIPS') or r.get('county_fips')}, Spec: {r.get('REQUIRED_SPECIALTY') or r.get('required_specialty')}, Count: {r.get('PROVIDER_COUNT') or r.get('provider_count')}")
except Exception as e:
    print(f"   [FAIL] Supply query error: {e}")

print("\n==================================================")
print("DIAGNOSTIC COMPLETED")
print("==================================================")
