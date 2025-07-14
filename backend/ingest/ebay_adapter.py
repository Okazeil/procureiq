import os
import requests
from dotenv import load_dotenv

load_dotenv()

EBAY_BASE_URL = "https://api.ebay.com/buy/browse/v1/item_summary/search"
EBAY_ACCESS_TOKEN = os.getenv("EBAY_ACCESS_TOKEN")

def search_ebay(query):
    if not EBAY_ACCESS_TOKEN:
        print("[ERROR] Missing eBay access token. Check your .env file.")
        return []

    headers = {
        "Authorization": EBAY_ACCESS_TOKEN,
        "Content-Type": "application/json",
    }

    params = {
        "q": query,
        "limit": "5",  # You can adjust this as needed
    }

    print(f"[INFO] Searching eBay for: {query}")
    try:
        response = requests.get(EBAY_BASE_URL, headers=headers, params=params)
        response.raise_for_status()
        data = response.json()

        if "itemSummaries" in data:
            return data["itemSummaries"]
        else:
            print("[WARN] No listings found or API failed.")
            return []

    except requests.exceptions.HTTPError as http_err:
        print(f"[ERROR] HTTP error occurred: {http_err}")
        print(f"[ERROR] Response: {response.text}")
        return []
    except Exception as err:
        print(f"[ERROR] Other error occurred: {err}")
        return []