# backend/api/main.py
from fastapi import FastAPI, Query, HTTPException
from fastapi import Header
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional
import os, sys
from pathlib import Path
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

# ------------------------------------------------------------------
# Make imports + .env loading work no matter where we run uvicorn from
# ------------------------------------------------------------------
HERE = Path(__file__).resolve()
PROJECT_ROOT = HERE.parents[2]          # .../procureiq
ENV_PATH = PROJECT_ROOT / ".env"
API_KEY_EXPECTED = os.getenv("PROCUREIQ_API_KEY")

# Ensure project root on sys.path so "backend...." imports always work
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# Load .env from project root explicitly
load_dotenv(ENV_PATH)

# Now safe to import our internal modules
from backend.ingest.ebay_adapter import search_ebay
from backend.ingest.db_utils import create_listings_table, insert_listings

app = FastAPI(title="ProcureIQ API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],           # tighten later
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DB_CONFIG = {
    "dbname": os.getenv("POSTGRES_DB"),
    "user": os.getenv("POSTGRES_USER"),
    "password": os.getenv("POSTGRES_PASSWORD"),
    "host": os.getenv("POSTGRES_HOST", "localhost"),
    "port": int(os.getenv("POSTGRES_PORT", "5432")),
}

def get_conn():
    return psycopg2.connect(**DB_CONFIG, cursor_factory=RealDictCursor)

@app.on_event("startup")
def startup():
    try:
        create_listings_table()
        print("[INFO] DB ready; listings table ensured.")
    except Exception as e:
        print(f"[WARN] create_listings_table failed: {e}")

@app.get("/")
def root():
    return {"name": "ProcureIQ API", "docs": "/docs"}

@app.get("/health")
def health():
    try:
        with get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT 1;")
        return {"status": "ok"}
    except Exception as e:
        return {"status": "error", "detail": str(e)}

@app.get("/search")
def search(term: str = Query(..., min_length=2), limit: int = Query(10, ge=1, le=50)):
    sql = """
        SELECT title, price_value, currency, item_url, created_at
        FROM listings
        WHERE title ILIKE %s
        ORDER BY created_at DESC
        LIMIT %s;
    """
    try:
        with get_conn() as conn, conn.cursor() as cur:
            cur.execute(sql, (f"%{term}%", limit))
            rows = cur.fetchall()
        return {"count": len(rows), "results": rows}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/ingest")
def ingest(
    term: str = Query(..., min_length=2),
    limit: int = Query(10, ge=1, le=50),
    x_api_key: str | None = Header(default=None)
):
    # Simple API-key guard (only enforced if key is set in .env)
    if API_KEY_EXPECTED:
        if not x_api_key or x_api_key != API_KEY_EXPECTED:
            raise HTTPException(status_code=401, detail="Unauthorized")

    try:
        items = search_ebay(term)
        if not items:
            return {"ingested": 0, "message": "No results from eBay (or API error)."}

        items = items[:limit]
        insert_listings(items)
        return {"ingested": len(items), "term": term}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))