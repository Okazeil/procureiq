import os
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

load_dotenv()

DB_CONFIG = {
    "dbname": os.getenv("POSTGRES_DB"),
    "user": os.getenv("POSTGRES_USER"),
    "password": os.getenv("POSTGRES_PASSWORD"),
    "host": os.getenv("POSTGRES_HOST", "localhost"),
    "port": os.getenv("POSTGRES_PORT", 5432),
}

def search_listings(term):
    query = """
        SELECT title, price_value, currency, item_url
        FROM listings
        WHERE title ILIKE %s
        ORDER BY created_at DESC
        LIMIT 10;
    """
    with psycopg2.connect(**DB_CONFIG) as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(query, (f"%{term}%",))
            return cur.fetchall()

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python search_listings.py 'keyword'")
        sys.exit(1)

    term = sys.argv[1]
    results = search_listings(term)

    if not results:
        print("[WARN] No matches found.")
    else:
        print(f"[INFO] {len(results)} match(es):\n")
        for r in results:
            print(f"- {r['title']} | {r['price_value']} {r['currency']}")
            print(f"  {r['item_url']}\n")