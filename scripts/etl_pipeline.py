import os
import glob
import json
import pandas as pd
import psycopg
from dotenv import load_dotenv

# Load credentials from .env
load_dotenv()

DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "forestwatch")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD")

CONN_STR = f"host={DB_HOST} port={DB_PORT} dbname={DB_NAME} user={DB_USER} password={DB_PASSWORD}"

def log_validation(source_file, processed, failed, status):
    """Logs pipeline execution metrics into validation_logs."""
    with psycopg.connect(CONN_STR) as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO validation_logs (source_file, records_processed, records_failed, status)
                VALUES (%s, %s, %s, %s);
                """,
                (source_file, processed, failed, status)
            )
        conn.commit()

def parse_confidence(val):
    """Converts FIRMS confidence string or numeric value to float."""
    try:
        return float(val)
    except (ValueError, TypeError):
        mapping = {'l': 30.0, 'n': 50.0, 'h': 90.0}
        return mapping.get(str(val).lower(), 50.0)

def run_etl():
    print("Starting Complete ETL Data Ingestion Pipeline...")

    # 1. Ingest Sample CSV Files
    sample_forest = os.path.join("data", "forest_loss.csv")
    if os.path.exists(sample_forest):
        ingest_forest_csv(sample_forest)

    sample_fire = os.path.join("data", "fire_alerts.csv")
    if os.path.exists(sample_fire):
        ingest_fire_csv(sample_fire)

    # 2. Ingest FIRMS API CSV files in scripts directory
    firms_files = glob.glob(os.path.join("scripts", "**", "firms_*.csv"), recursive=True) + glob.glob(os.path.join("scripts", "firms_*.csv"))
    for ffile in set(firms_files):
        ingest_firms_csv(ffile)

    # 3. Ingest GFW API JSON files in scripts directory
    gfw_files = glob.glob(os.path.join("scripts", "**", "gfw_*.json"), recursive=True) + glob.glob(os.path.join("scripts", "gfw_*.json"))
    for gfile in set(gfw_files):
        if not gfile.endswith(".meta.json"):
            ingest_gfw_json(gfile)

    print("Complete ETL Pipeline finished successfully!")

def ingest_forest_csv(filepath):
    try:
        df = pd.read_csv(filepath)
        processed, failed = 0, 0
        with psycopg.connect(CONN_STR) as conn:
            with conn.cursor() as cur:
                for _, row in df.iterrows():
                    try:
                        cur.execute(
                            "INSERT INTO forest_loss (region, country, year, area_ha) VALUES (%s, %s, %s, %s);",
                            (row['region'], row['country'], int(row['year']), float(row['area_ha']))
                        )
                        processed += 1
                    except Exception:
                        failed += 1
            conn.commit()
        status = "SUCCESS" if failed == 0 else "PARTIAL"
        log_validation(os.path.basename(filepath), processed, failed, status)
        print(f"Loaded {processed} records from {os.path.basename(filepath)} into 'forest_loss'.")
    except Exception as e:
        print(f"Failed processing {filepath}: {e}")
        log_validation(os.path.basename(filepath), 0, 0, "FAILED")

def ingest_fire_csv(filepath):
    try:
        df = pd.read_csv(filepath)
        processed, failed = 0, 0
        with psycopg.connect(CONN_STR) as conn:
            with conn.cursor() as cur:
                for _, row in df.iterrows():
                    try:
                        cur.execute(
                            "INSERT INTO fire_alerts (latitude, longitude, confidence, alert_date) VALUES (%s, %s, %s, %s);",
                            (float(row['latitude']), float(row['longitude']), parse_confidence(row['confidence']), str(row['alert_date']))
                        )
                        processed += 1
                    except Exception:
                        failed += 1
            conn.commit()
        status = "SUCCESS" if failed == 0 else "PARTIAL"
        log_validation(os.path.basename(filepath), processed, failed, status)
        print(f"Loaded {processed} records from {os.path.basename(filepath)} into 'fire_alerts'.")
    except Exception as e:
        print(f"Failed processing {filepath}: {e}")
        log_validation(os.path.basename(filepath), 0, 0, "FAILED")

def ingest_firms_csv(filepath):
    try:
        df = pd.read_csv(filepath)
        processed, failed = 0, 0
        with psycopg.connect(CONN_STR) as conn:
            with conn.cursor() as cur:
                for _, row in df.iterrows():
                    try:
                        cur.execute(
                            "INSERT INTO fire_alerts (latitude, longitude, confidence, alert_date) VALUES (%s, %s, %s, %s);",
                            (float(row['latitude']), float(row['longitude']), parse_confidence(row['confidence']), str(row['acq_date']))
                        )
                        processed += 1
                    except Exception:
                        failed += 1
            conn.commit()
        status = "SUCCESS" if failed == 0 else "PARTIAL"
        log_validation(os.path.basename(filepath), processed, failed, status)
        print(f"Loaded {processed} records from FIRMS file '{os.path.basename(filepath)}' into 'fire_alerts'.")
    except Exception as e:
        print(f"Failed processing FIRMS file {filepath}: {e}")
        log_validation(os.path.basename(filepath), 0, 0, "FAILED")

def ingest_gfw_json(filepath):
    try:
        with open(filepath, 'r') as f:
            content = json.load(f)
        
        data_items = content.get("data", [])
        processed, failed = 0, 0
        
        country = "Australia" if "AUS" in filepath else "Unknown"
        region = "AUS" if "AUS" in filepath else "Global"
        
        with psycopg.connect(CONN_STR) as conn:
            with conn.cursor() as cur:
                for item in data_items:
                    try:
                        cur.execute(
                            "INSERT INTO forest_loss (region, country, year, area_ha) VALUES (%s, %s, %s, %s);",
                            (region, country, int(item['year']), float(item['area_ha']))
                        )
                        processed += 1
                    except Exception:
                        failed += 1
            conn.commit()
        status = "SUCCESS" if failed == 0 else "PARTIAL"
        log_validation(os.path.basename(filepath), processed, failed, status)
        print(f"Loaded {processed} records from GFW file '{os.path.basename(filepath)}' into 'forest_loss'.")
    except Exception as e:
        print(f"Failed processing GFW file {filepath}: {e}")
        log_validation(os.path.basename(filepath), 0, 0, "FAILED")

if __name__ == "__main__":
    run_etl()