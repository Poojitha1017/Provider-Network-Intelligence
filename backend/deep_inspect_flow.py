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

print("==================================================")
print("COMPREHENSIVE SUPABASE DATA RELATIONSHIP AUDIT")
print("==================================================")

# 1. Inspect decision table
d_res = client.table("decision").select("*").limit(10).execute()
print(f"1. Decision Sample (Total rows sample: {len(d_res.data)}):")
for r in d_res.data[:2]:
    print(json.dumps(r, indent=2, default=str))

# 2. Inspect supply table
s_res = client.table("supply").select("*").limit(10).execute()
print(f"\n2. Supply Sample (Total rows sample: {len(s_res.data)}):")
for r in s_res.data[:2]:
    print(json.dumps(r, indent=2, default=str))

# 3. Inspect providers table
p_res = client.table("providers").select("*").limit(10).execute()
print(f"\n3. Providers Sample (Total rows sample: {len(p_res.data)}):")
for r in p_res.data[:2]:
    print(json.dumps(r, indent=2, default=str))

# 4. Inspect provider_service_areas table
psa_res = client.table("provider_service_areas").select("*").limit(10).execute()
print(f"\n4. Provider Service Areas Sample (Total rows sample: {len(psa_res.data)}):")
for r in psa_res.data[:2]:
    print(json.dumps(r, indent=2, default=str))

# 5. Inspect uc05_filter_options table
f_res = client.table("uc05_filter_options").select("*").limit(10).execute()
print(f"\n5. Filter Options Sample (Total rows sample: {len(f_res.data)}):")
for r in f_res.data[:2]:
    print(json.dumps(r, indent=2, default=str))

# Check join between providers and provider_service_areas
sample_npi = psa_res.data[0]["NPI"] if psa_res.data else None
if sample_npi:
    p_match = client.table("providers").select("*").eq("NPI", sample_npi).execute()
    print(f"\n6. Join Check on NPI '{sample_npi}':")
    print(f"   Matches in providers: {len(p_match.data)}")

# Check join between decision and supply
sample_fips = d_res.data[0]["COUNTY_FIPS"] if d_res.data else None
sample_spec = d_res.data[0]["REQUIRED_SPECIALTY"] if d_res.data else None
if sample_fips and sample_spec:
    s_match = client.table("supply").select("*").eq("COUNTY_FIPS", sample_fips).eq("REQUIRED_SPECIALTY", sample_spec).execute()
    print(f"\n7. Join Check between Decision and Supply (FIPS '{sample_fips}', Spec '{sample_spec}'):")
    print(f"   Matches in supply: {len(s_match.data)}")
    if s_match.data:
        print(f"   Supply row: {s_match.data[0]}")

# Check distinct states, cities in filter_options vs providers
f_states = client.table("uc05_filter_options").select("state").limit(100).execute()
distinct_f_states = set(r["state"] for r in f_states.data)
p_states = client.table("providers").select("STATE").limit(100).execute()
distinct_p_states = set(r["STATE"] for r in p_states.data)
d_states = client.table("decision").select("STATEDESC").limit(100).execute()
distinct_d_states = set(r["STATEDESC"] for r in d_states.data)

print(f"\n8. State representation check:")
print(f"   uc05_filter_options 'state': {distinct_f_states}")
print(f"   providers 'STATE': {distinct_p_states}")
print(f"   decision 'STATEDESC': {distinct_d_states}")
