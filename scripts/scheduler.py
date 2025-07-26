import schedule
import time
import subprocess

# Your list of recurring search terms
SEARCH_TERMS = [
    # Dell Servers & Chassis
    "PowerEdge", "R620", "R630", "R640", "R650", "R720", "R730", "R740", "R750", "T320", "T330", "T340", "T420", "T430", "T440",
    "M610", "M620", "M630", "C6100", "C6220", "FX2", "Dell Chassis",

    # HP ProLiant Servers
    "ProLiant", "DL160", "DL180", "DL360", "DL380", "DL385", "DL560", "ML110", "ML150", "ML350", "BL460c", "HP Blade",

    # IBM & Lenovo
    "IBM x3550", "IBM x3650", "System x", "Lenovo ThinkSystem", "SR550", "SR630", "SR650",

    # Supermicro & Other Whitebox Servers
    "Supermicro", "1U Server", "2U Server", "4U Server", "Server Chassis", "Barebone Server", "Rackmount Server",

    # CPUs
    "Xeon", "E5-2620", "E5-2630", "E5-2650", "E5-2670", "E5-2680", "E5-2690", "E5-2699", "E3-1230", "E3-1240", "Platinum 8260", "Gold 6130",

    # Storage Arrays & JBODs
    "MD1200", "MD1220", "MD1400", "MD1420", "NetApp", "DS2246", "DS4246", "EMC KTN-STL3", "EMC DAEs", "Dell Compellent", "Hitachi G1000",

    # Storage Controllers / Adapters
    "PERC H700", "PERC H710", "PERC H730", "PERC H740", "LSI 9207", "LSI 9211", "RAID Controller", "HBA", "SAS HBA", "SATA HBA",

    # Misc Keywords for Broader Coverage
    "Refurbished Server", "Used Server", "Data Center Server", "Enterprise Server", "Server PSU", "Server RAM", "Server Parts", "Server Lot"
]

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