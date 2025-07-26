import schedule
import time
import subprocess

# Your list of recurring search terms
SEARCH_TERMS = ["R750", "DL380", "PowerEdge", "Xeon"]

def run_ingestion():
    for term in SEARCH_TERMS:
        print(f"[INFO] Running ingestion for: {term}")
        subprocess.run(["python", "backend/ingest/run_ingestion.py", term])

# Schedule the task every hour
schedule.every(1).hours.do(run_ingestion)

print("[INFO] Scheduler started. Running every 1 hour...")

while True:
    schedule.run_pending()
    time.sleep(60)