import os
import sys
from dotenv import load_dotenv

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
load_dotenv()

from supabase import create_client

url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_SERVICE_ROLE_KEY") or os.getenv("SUPABASE_ANON_KEY")
client = create_client(url, key)

res = client.table("uc05_filter_options").select("county_fips, city, state").limit(2000).execute()
fips_to_city = {}
city_to_fips = {}
for r in res.data:
    f = r.get("county_fips")
    c = r.get("city")
    if f and c:
        fips_to_city[str(f)] = str(c).upper()
        city_to_fips[str(c).upper()] = str(f)

print(f"Total unique FIPS in filter_options: {len(fips_to_city)}")
print(f"Sample mappings:")
for k, v in list(fips_to_city.items())[:10]:
    print(f"   FIPS {k} <--> City {v}")
