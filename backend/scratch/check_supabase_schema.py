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

print("Checking Supabase connection and tables...")
for table_name in ["providers", "decision", "supply", "provider_service_areas"]:
    try:
        res = client.table(table_name).select("*", count="exact").limit(1).execute()
        print(f"Table '{table_name}': Count={res.count}")
    except Exception as e:
        print(f"Table '{table_name}': Error - {e}")
