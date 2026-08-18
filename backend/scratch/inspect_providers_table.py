import os
import sys
import json
from dotenv import load_dotenv
from supabase import create_client

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
load_dotenv()

url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_SERVICE_ROLE_KEY") or os.getenv("SUPABASE_ANON_KEY")
client = create_client(url, key)

res = client.table("providers").select("STATE, COUNTY_FIPS, COUNTY, PRIMARY_SPECIALTY, DISEASE, RISK_SCORE, ACCESS_LEVEL", count="exact").limit(10).execute()

print(f"Total providers in Supabase: {res.count}")
print("Sample 10 provider rows:")
for r in res.data:
    print(r)

# Check distinct states in providers table
all_states = client.table("providers").select("STATE").limit(2000).execute()
states_set = set(r["STATE"] for r in all_states.data if r.get("STATE"))
print(f"\nDistinct STATES in 'providers' table: {states_set}")

# Check distinct specialties in providers table
all_specs = client.table("providers").select("PRIMARY_SPECIALTY").limit(2000).execute()
specs_set = set(r["PRIMARY_SPECIALTY"] for r in all_specs.data if r.get("PRIMARY_SPECIALTY"))
print(f"Distinct PRIMARY_SPECIALTY in 'providers' table: {specs_set}")

# Check distinct diseases in providers table
all_dis = client.table("providers").select("DISEASE").limit(2000).execute()
dis_set = set(r["DISEASE"] for r in all_dis.data if r.get("DISEASE"))
print(f"Distinct DISEASE in 'providers' table: {dis_set}")
