import os
import sys
from dotenv import load_dotenv

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
load_dotenv()

from supabase import create_client

url = os.getenv("SUPABASE_URL")
anon_key = os.getenv("SUPABASE_ANON_KEY")

client = create_client(url, anon_key)

for table in ["supply", "decision", "uc05_filter_options", "providers"]:
    try:
        res = client.table(table).select("*").limit(2).execute()
        print(f"Table '{table}' with anon key: OK ({len(res.data)} rows)")
    except Exception as e:
        print(f"Table '{table}' with anon key: ERROR -> {e}")
