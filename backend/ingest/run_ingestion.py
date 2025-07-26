import sys
import json
import os
from pathlib import Path

from backend.ingest.ebay_adapter import search_ebay
from .db_utils import create_listings_table, insert_listings
from dotenv import load_dotenv

load_dotenv()

def main():
    if len(sys.argv) < 2:
        print("Usage: python run_ingestion.py \"search term\"")
        sys.exit(1)

    query = sys.argv[1]
    print(f"[INFO] Searching eBay for: {query}")

    results = search_ebay(query)

    if not results:
        print("[WARN] No listings found or API failed.")
        return

    # Optional: Save to local JSON (for testing or logging)
    data_dir = Path("data")
    data_dir.mkdir(exist_ok=True)
    filename = data_dir / f"{query.replace(' ', '_')}.json"
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)
    print(f"[✓] Saved {len(results)} listings to: {filename}")

    # ✅ Save to PostgreSQL
    create_listings_table()
    insert_listings(results)

if __name__ == "__main__":
    main()