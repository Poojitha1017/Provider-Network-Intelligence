import os
import sys
import csv
import json
import logging
from dotenv import load_dotenv
from supabase import create_client

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
load_dotenv()

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("SupabaseSeeder")

url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_SERVICE_ROLE_KEY") or os.getenv("SUPABASE_ANON_KEY")

if not url or not key:
    logger.error("Supabase URL or Key missing in .env")
    sys.exit(1)

client = create_client(url, key)
logger.info(f"Connected to Supabase project at {url}")

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")

def seed_table(table_name: str, csv_filename: str):
    csv_path = os.path.join(DATA_DIR, csv_filename)
    if not os.path.exists(csv_path):
        logger.warning(f"File not found: {csv_path}")
        return

    records = []
    with open(csv_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for r in reader:
            records.append(r)

    logger.info(f"Seeding {len(records)} records into Supabase table '{table_name}'...")
    
    # Upsert in batches of 200
    batch_size = 200
    success_count = 0
    for i in range(0, len(records), batch_size):
        batch = records[i:i + batch_size]
        try:
            res = client.table(table_name).upsert(batch).execute()
            success_count += len(batch)
        except Exception as e:
            logger.error(f"Error seeding batch into {table_name}: {e}")

    logger.info(f"[DONE] Table '{table_name}': {success_count}/{len(records)} records upserted successfully.")

if __name__ == "__main__":
    print("==========================================================")
    print("   SEEDING CLEANED DATASETS INTO SUPABASE DATABASE")
    print("==========================================================")
    
    seed_table("providers", "UC05_PROVIDERS_CLEANED.csv")
    seed_table("decision", "UC05_DECISION_CLEANED.csv")
    seed_table("supply", "UC05_SUPPLY_CLEANED.csv")
    seed_table("provider_service_areas", "UC05_SERVICE_AREAS_CLEANED.csv")
    
    print("\n[SUCCESS] Seeding script execution complete.")
