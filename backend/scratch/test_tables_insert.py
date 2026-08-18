import os
import sys
from dotenv import load_dotenv
from supabase import create_client

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
load_dotenv()

url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_SERVICE_ROLE_KEY") or os.getenv("SUPABASE_ANON_KEY")
client = create_client(url, key)

tables = ["providers", "decision", "supply", "provider_service_areas", "uc05_filter_options", "profiles"]

for tbl in tables:
    try:
        # Dry run or count check
        res = client.table(tbl).select("*", count="exact").limit(1).execute()
        print(f"Table '{tbl}': SELECT PASS, count={res.count}")
    except Exception as e:
        print(f"Table '{tbl}': SELECT FAIL - {e}")

print("\nTesting INSERT privileges...")

# Test insert into providers
try:
    test_prov = {
        "NPI": "9999999999",
        "PROVIDER_NAME": "TEST PROVIDER",
        "PRIMARY_SPECIALTY": "Cardiology",
        "STATE": "TX",
        "ZIP": "75601",
        "COUNTY_FIPS": "48183",
        "COUNTY": "Gregg County",
        "DISEASE": "Heart Disease"
    }
    res = client.table("providers").insert(test_prov).execute()
    print("Table 'providers': INSERT PASS")
    # Clean up test row
    client.table("providers").delete().eq("NPI", "9999999999").execute()
except Exception as e:
    print(f"Table 'providers': INSERT FAIL - {e}")

# Test insert into decision
try:
    test_dec = {
        "COUNTY_FIPS": "99999",
        "STATEDESC": "Texas",
        "REQUIRED_SPECIALTY": "Cardiology",
        "ESTIMATED_PATIENTS": 1000,
        "PROVIDER_COUNT": 1,
        "GAP_SCORE": 50.0
    }
    res = client.table("decision").insert(test_dec).execute()
    print("Table 'decision': INSERT PASS")
    client.table("decision").delete().eq("COUNTY_FIPS", "99999").execute()
except Exception as e:
    print(f"Table 'decision': INSERT FAIL - {e}")

# Test insert into supply
try:
    test_sup = {
        "COUNTY_FIPS": "99999",
        "REQUIRED_SPECIALTY": "Cardiology",
        "PROVIDER_COUNT": 1
    }
    res = client.table("supply").insert(test_sup).execute()
    print("Table 'supply': INSERT PASS")
    client.table("supply").delete().eq("COUNTY_FIPS", "99999").execute()
except Exception as e:
    print(f"Table 'supply': INSERT FAIL - {e}")
