import os
import psycopg
from dotenv import load_dotenv

load_dotenv()

DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "forestwatch")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD")

conn_str = f"host={DB_HOST} port={DB_PORT} dbname={DB_NAME} user={DB_USER} password={DB_PASSWORD}"

try:
    with psycopg.connect(conn_str) as conn:
        with conn.cursor() as cur:
            print("Creating database indexes...")
            cur.execute("CREATE INDEX IF NOT EXISTS idx_fire_alerts_date ON fire_alerts(alert_date);")
            cur.execute("CREATE INDEX IF NOT EXISTS idx_fire_alerts_location ON fire_alerts(latitude, longitude);")
            cur.execute("CREATE INDEX IF NOT EXISTS idx_forest_loss_country_year ON forest_loss(country, year);")
        conn.commit()
        print("Database indexes created successfully!")
except Exception as e:
    print(f"Error creating indexes: {e}")