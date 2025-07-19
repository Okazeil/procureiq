import os
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

load_dotenv()

def get_db_connection():
    """Create and return a connection to the PostgreSQL database."""
    return psycopg2.connect(
        dbname=os.getenv("POSTGRES_DB"),
        user=os.getenv("POSTGRES_USER"),
        password=os.getenv("POSTGRES_PASSWORD"),
        host=os.getenv("POSTGRES_HOST", "localhost"),
        port=os.getenv("POSTGRES_PORT", 5432)
    )

def create_listings_table():
    """Create the listings table if it doesn't already exist."""
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS listings (
            id SERIAL PRIMARY KEY,
            title TEXT,
            price_value NUMERIC,
            currency TEXT,
            item_url TEXT,
            image_url TEXT,
            seller TEXT,
            source TEXT DEFAULT 'eBay',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)

    conn.commit()
    cur.close()
    conn.close()

def insert_listings(listings):
    """Insert a list of eBay listings into the database."""
    if not listings:
        print("[WARN] No listings to insert.")
        return

    conn = get_db_connection()
    cur = conn.cursor()

    for item in listings:
        title = item.get("title")
        price = item.get("price", {})
        price_value = price.get("value")
        currency = price.get("currency")
        item_url = item.get("itemWebUrl")
        image_url = item.get("image", {}).get("imageUrl")
        seller = item.get("seller", {}).get("username")

        cur.execute("""
            INSERT INTO listings (title, price_value, currency, item_url, image_url, seller)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (title, price_value, currency, item_url, image_url, seller))

    conn.commit()
    cur.close()
    conn.close()
    print(f"[✓] Inserted {len(listings)} listings into database.")