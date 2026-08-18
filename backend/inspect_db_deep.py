import os
import sys
import json
from dotenv import load_dotenv

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
load_dotenv()

from supabase import create_client

url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_SERVICE_ROLE_KEY") or os.getenv("SUPABASE_ANON_KEY")

client = create_client(url, key)

print("--- Inspecting decision table samples ---")
res = client.table("decision").select("*").limit(5).execute()
for r in res.data:
    print(json.dumps(r, indent=2, default=str))

print("\n--- Unique ACCESS_GAP_LEVEL in decision table ---")
res_levels = client.table("decision").select("ACCESS_GAP_LEVEL").limit(1000).execute()
levels = set(r.get("ACCESS_GAP_LEVEL") for r in res_levels.data)
print("Levels in DB:", levels)

print("\n--- Unique Specialties in decision table ---")
res_specs = client.table("decision").select("REQUIRED_SPECIALTY").limit(1000).execute()
specs = set(r.get("REQUIRED_SPECIALTY") for r in res_specs.data)
print("Specialties in DB:", specs)

print("\n--- Checking coordinates in providers table ---")
p_res = client.table("providers").select("COUNTY_FIPS, STATE, CITY, latitude, longitude").not_.is_("latitude", "null").limit(5).execute()
print(f"Providers with coordinates ({len(p_res.data)}):", p_res.data)
