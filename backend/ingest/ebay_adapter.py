import os
import requests
import base64
import json
import time
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

CACHE_PATH = Path(".token_cache.json")


EBAY_API_URL = "https://api.ebay.com/buy/browse/v1/item_summary/search"

def get_ebay_access_token():
    """Returns a cached token if valid, or fetches a new one if expired."""

    # === STEP 1: Try loading token from cache ===
    if CACHE_PATH.exists():
        with open(CACHE_PATH, "r") as f:
            cache = json.load(f)
            token = cache.get("access_token")
            expires_at = cache.get("expires_at")

            if token and expires_at and time.time() < expires_at:
                return f"Bearer {token}"  # ✅ Valid token

    # === STEP 2: Fetch new token from eBay ===
    print("[INFO] Fetching fresh access token from eBay...")

    client_id = os.getenv("EBAY_APP_ID")
    client_secret = os.getenv("EBAY_CERT_ID")

    if not client_id or not client_secret:
        raise ValueError("[ERROR] Missing EBAY_APP_ID or EBAY_CERT_ID in .env")

    credentials = f"{client_id}:{client_secret}"
    encoded_credentials = base64.b64encode(credentials.encode()).decode()

    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Authorization": f"Basic {encoded_credentials}"
    }

    data = {
        "grant_type": "client_credentials",
        "scope": "https://api.ebay.com/oauth/api_scope"
    }

    response = requests.post("https://api.ebay.com/identity/v1/oauth2/token", headers=headers, data=data)
    response.raise_for_status()

    res_json = response.json()
    token = res_json["access_token"]
    expires_in = res_json.get("expires_in", 7200)  # Default: 2 hours

    # Save to cache
    with open(CACHE_PATH, "w") as f:
        json.dump({
            "access_token": token,
            "expires_at": time.time() + expires_in - 60  # Refresh 1 min early
        }, f)

    return f"Bearer {token}"

def search_ebay(query):
    """Search eBay using the Browse API and a fresh access token."""
    access_token = get_ebay_access_token()

    headers = {
        "Authorization": access_token,
        "Content-Type": "application/json",
        "X-EBAY-C-MARKETPLACE-ID": "EBAY_GB"
    }

    params = {
        "q": query,
        "limit": "5",
    }

    print(f"[INFO] Searching eBay for: {query}")
    try:
        response = requests.get(EBAY_API_URL, headers=headers, params=params)
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