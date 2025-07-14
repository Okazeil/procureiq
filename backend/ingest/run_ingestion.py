import sys
import json
import os
from pathlib import Path
from backend.ingest.ebay_adapter import search_ebay

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

    # Ensure output directory exists at project root
    project_root = Path(__file__).resolve().parents[2]
    output_dir = project_root / "data"
    os.makedirs(output_dir, exist_ok=True)

    filename = f"{query.lower().replace(' ', '_')}.json"
    output_path = output_dir / filename

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)

    print(f"[✓] Saved {len(results)} listings to: {output_path}")


if __name__ == "__main__":
    main()