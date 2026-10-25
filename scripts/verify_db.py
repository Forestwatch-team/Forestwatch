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
            print("--- Forest Loss Records ---")
            cur.execute("SELECT COUNT(*) FROM forest_loss;")
            print(f"Total rows: {cur.fetchone()[0]}")

            print("\n--- Fire Alerts Records ---")
            cur.execute("SELECT COUNT(*) FROM fire_alerts;")
            print(f"Total rows: {cur.fetchone()[0]}")

            print("\n--- Validation Logs ---")
            cur.execute("SELECT source_file, records_processed, records_failed, status FROM validation_logs;")
            for row in cur.fetchall():
                print(f"File: {row[0]} | Processed: {row[1]} | Failed: {row[2]} | Status: {row[3]}")
except Exception as e:
    print(f"Database error: {e}")