import os
import psycopg
from dotenv import load_dotenv

load_dotenv()

DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")

def create_indexes():
    queries = [
        "CREATE INDEX IF NOT EXISTS idx_fire_alerts_date ON fire_alerts(acq_date);",
        "CREATE INDEX IF NOT EXISTS idx_fire_alerts_location ON fire_alerts(latitude, longitude);",
        "CREATE INDEX IF NOT EXISTS idx_forest_loss_country_year ON forest_loss(country, year);"
    ]
    try:
        print("Creating database indexes...")
        with psycopg.connect(
            host=DB_HOST,
            port=DB_PORT,
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            prepare_threshold=None
        ) as conn:
            with conn.cursor() as cur:
                for q in queries:
                    cur.execute(q)
                conn.commit()
        print("Database indexes created successfully!")
    except Exception as e:
        print(f"Error creating indexes: {e}")

if __name__ == "__main__":
    create_indexes()