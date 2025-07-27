import sys
import json
import os
from pathlib import Path

from backend.ingest.ebay_adapter import search_ebay
from .db_utils import create_listings_table, insert_listings
from dotenv import load_dotenv
from backend.ingest.relevance import is_semantically_similar  # ✅ New import

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

    # 🧠 Filter results using semantic similarity
    # 🔍 TEMPORARY: Skip filtering to confirm raw results
    #print(f"[DEBUG] Ingesting all {len(results)} listings without filtering.")
    #filtered_results = results
    
    filtered_results = []
    for result in results:
        title = result.get("title", "")
        if is_semantically_similar(title, query):
            filtered_results.append(result)
        else:
            print(f"[SKIP] Not similar: {title}")

    if not filtered_results:
        print("[INFO] No listings passed semantic filtering.")
        return

    # # Disabled JSON saving
    # data_dir = Path("data")
    # data_dir.mkdir(exist_ok=True)
    # filename = data_dir / f"{query.replace(' ', '_')}.json"
    # with open(filename, "w", encoding="utf-8") as f:
    #     json.dump(filtered_results, f, indent=2)
    # print(f"[✓] Saved {len(filtered_results)} listings to: {filename}")

    # ✅ Save to PostgreSQL
    create_listings_table()
    insert_listings(filtered_results)

if __name__ == "__main__":
    main()