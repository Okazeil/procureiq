# scripts/scheduler.py
import os
import time
import random
import requests
import schedule
from dotenv import load_dotenv

load_dotenv()

# === Config ===
API_BASE = os.getenv("PROCUREIQ_API_URL", "http://127.0.0.1:8000")
API_KEY = os.getenv("PROCUREIQ_API_KEY")  # optional; see FastAPI patch below
LIMIT = int(os.getenv("INGEST_LIMIT", "10"))
CADENCE_MINUTES = int(os.getenv("INGEST_EVERY_MINUTES", "60"))  # default: hourly

# Use your existing mega list; paste yours below or import from a file.
SEARCH_TERMS = [
    # Dell Servers & Chassis
    "PowerEdge", "R620", "R630", "R640", "R650", "R720", "R730", "R740", "R750",
    "T320", "T330", "T340", "T420", "T430", "T440",
    "M610", "M620", "M630", "C6100", "C6220", "FX2", "Dell Chassis",

    # HP ProLiant Servers
    "ProLiant", "DL160", "DL180", "DL360", "DL380", "DL385", "DL560",
    "ML110", "ML150", "ML350", "BL460c", "HP Blade",

    # IBM / Lenovo
    "IBM x3550", "IBM x3650", "System x", "Lenovo ThinkSystem", "SR550", "SR630", "SR650",

    # Supermicro / Whitebox
    "Supermicro", "1U Server", "2U Server", "4U Server", "Server Chassis", "Barebone Server", "Rackmount Server",

    # CPUs
    "Xeon", "E5-2620", "E5-2630", "E5-2650", "E5-2670", "E5-2680", "E5-2690", "E5-2699",
    "E3-1230", "E3-1240", "Platinum 8260", "Gold 6130",

    # Storage / HBAs / Controllers
    "MD1200", "MD1220", "MD1400", "MD1420", "NetApp", "DS2246", "DS4246",
    "EMC KTN-STL3", "EMC DAEs", "Dell Compellent", "Hitachi G1000",
    "PERC H700", "PERC H710", "PERC H730", "PERC H740", "LSI 9207", "LSI 9211",
    "RAID Controller", "HBA", "SAS HBA", "SATA HBA",

    # Broader / lots
    "Refurbished Server", "Used Server", "Data Center Server", "Enterprise Server",
    "Server PSU", "Server RAM", "Server Parts", "Server Lot",
]

def run_ingestion_once():
    headers = {}
    if API_KEY:
        headers["X-API-Key"] = API_KEY

    for term in SEARCH_TERMS:
        try:
            print(f"[INFO] Ingest via API -> {term}")
            r = requests.post(
                f"{API_BASE}/ingest",
                params={"term": term, "limit": LIMIT},
                headers=headers,
                timeout=90,
            )
            r.raise_for_status()
            print(f"[OK] {term}: {r.json()}")
        except requests.RequestException as e:
            print(f"[ERROR] {term}: {e}")
        # small jitter so we don’t fire everything at once
        time.sleep(random.uniform(1.0, 2.5))

def schedule_job():
    run_ingestion_once()

print(f"[INFO] Scheduler started. Calling {API_BASE}/ingest every {CADENCE_MINUTES} minute(s).")
# run one pass immediately (optional)
run_ingestion_once()

schedule.every(CADENCE_MINUTES).minutes.do(schedule_job)

while True:
    schedule.run_pending()
    time.sleep(1)