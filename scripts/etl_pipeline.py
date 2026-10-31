import os
import csv
import glob
import json
import pandas as pd
import psycopg
from dotenv import load_dotenv

load_dotenv()

DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "forestwatch")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "forestwatchadmin3@@@")

CONN_STR = f"host={DB_HOST} port={DB_PORT} dbname={DB_NAME} user={DB_USER} password={DB_PASSWORD}"

def log_validation(source_file, processed, failed, status):
    """Logs pipeline execution metrics into validation_logs."""
    with psycopg.connect(CONN_STR, prepare_threshold=None) as conn:
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

def is_valid_fire_alert(lat, lon, conf):
    """Validates spatial coordinates and confidence values."""
    if not (-90.0 <= lat <= 90.0):
        return False
    if not (-180.0 <= lon <= 180.0):
        return False
    if not (0.0 <= conf <= 100.0):
        return False
    return True

def is_valid_forest_loss(area_ha):
    """Validates forest loss area."""
    return area_ha > 0

def run_etl():
    print("Starting Validated & Deduplicated ETL Pipeline...")

    # 1. Ingest Sample CSV Files
    sample_forest = os.path.join("data", "forest_loss.csv")
    if os.path.exists(sample_forest):
        ingest_forest_csv(sample_forest)

    sample_fire = os.path.join("data", "fire_alerts.csv")
    if os.path.exists(sample_fire):
        ingest_fire_csv(sample_fire)

    # 2. Ingest FIRMS API CSV files
    firms_files = glob.glob(os.path.join("scripts", "**", "firms_*.csv"), recursive=True) + glob.glob(os.path.join("scripts", "firms_*.csv"))
    for ffile in set(firms_files):
        ingest_firms_csv(ffile)

    # 3. Ingest GFW API JSON files
    gfw_files = glob.glob(os.path.join("scripts", "**", "gfw_*.json"), recursive=True) + glob.glob(os.path.join("scripts", "gfw_*.json"))
    for gfile in set(gfw_files):
        if not gfile.endswith(".meta.json"):
            ingest_gfw_json(gfile)

    print("Validated ETL Pipeline finished successfully!")

def ingest_forest_csv(filepath):
    try:
        df = pd.read_csv(filepath)
        processed, failed = 0, 0
        with psycopg.connect(CONN_STR) as conn:
            with conn.cursor() as cur:
                for _, row in df.iterrows():
                    try:
                        area = float(row['area_ha'])
                        if not is_valid_forest_loss(area):
                            failed += 1
                            continue

                        cur.execute(
                            """
                            INSERT INTO forest_loss (region, country, year, area_ha)
                            VALUES (%s, %s, %s, %s)
                            ON CONFLICT (region, country, year) DO NOTHING;
                            """,
                            (row['region'], row['country'], int(row['year']), area)
                        )
                        if cur.rowcount > 0:
                            processed += 1
                    except Exception:
                        failed += 1
            conn.commit()
        status = "SUCCESS" if failed == 0 else "PARTIAL"
        log_validation(os.path.basename(filepath), processed, failed, status)
        print(f"Loaded {processed} new records from '{os.path.basename(filepath)}' (Failed/Skipped: {failed}).")
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
                        lat, lon = float(row['latitude']), float(row['longitude'])
                        conf = parse_confidence(row['confidence'])

                        if not is_valid_fire_alert(lat, lon, conf):
                            failed += 1
                            continue

                        cur.execute(
                            """
                            INSERT INTO fire_alerts (latitude, longitude, confidence, alert_date)
                            VALUES (%s, %s, %s, %s)
                            ON CONFLICT (latitude, longitude, alert_date) DO NOTHING;
                            """,
                            (lat, lon, conf, str(row['alert_date']))
                        )
                        if cur.rowcount > 0:
                            processed += 1
                    except Exception:
                        failed += 1
            conn.commit()
        status = "SUCCESS" if failed == 0 else "PARTIAL"
        log_validation(os.path.basename(filepath), processed, failed, status)
        print(f"Loaded {processed} new records from '{os.path.basename(filepath)}' (Failed/Skipped: {failed}).")
    except Exception as e:
        print(f"Failed processing {filepath}: {e}")
        log_validation(os.path.basename(filepath), 0, 0, "FAILED")

def ingest_firms_csv(filepath):
    """Bulk ingest FIRMS CSV in fast 1,000-row batches."""
    if not os.path.exists(filepath):
        print(f"File not found: {filepath}")
        return

    # 1. Read all rows into memory first
    records = []
    with open(filepath, mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            records.append((
                float(row["latitude"]),
                float(row["longitude"]),
                float(row["bright_ti4"]),
                float(row["scan"]),
                float(row["track"]),
                row["acq_date"],
                row["acq_time"],
                row["satellite"],
                row["instrument"],
                row["confidence"],
                row["version"],
                float(row["bright_ti5"]),
                float(row["frp"]),
                row["daynight"]
            ))

    # 2. Upload in fast 1,000-row chunks
    try:
        with psycopg.connect(CONN_STR, prepare_threshold=None) as conn:
            with conn.cursor() as cur:
                batch_size = 1000
                for i in range(0, len(records), batch_size):
                    batch = records[i:i + batch_size]
                    cur.executemany(
                        """
                        INSERT INTO fire_alerts (
                            latitude, longitude, bright_ti4, scan, track,
                            acq_date, acq_time, satellite, instrument,
                            confidence, version, bright_ti5, frp, daynight
                        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
                        """,
                        batch
                    )
                    conn.commit()

        log_validation(os.path.basename(filepath), len(records), 0, "SUCCESS")
        print(f"Successfully processed FIRMS file: {len(records)} records inserted.")

    except Exception as e:
        print(f"Failed processing FIRMS file {filepath}: {e}")
        try:
            log_validation(os.path.basename(filepath), 0, 0, "FAILED")
        except Exception:
            pass

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
                        area = float(item['area_ha'])
                        if not is_valid_forest_loss(area):
                            failed += 1
                            continue

                        cur.execute(
                            """
                            INSERT INTO forest_loss (region, country, year, area_ha)
                            VALUES (%s, %s, %s, %s)
                            ON CONFLICT (region, country, year) DO NOTHING;
                            """,
                            (region, country, int(item['year']), area)
                        )
                        if cur.rowcount > 0:
                            processed += 1
                    except Exception:
                        failed += 1
            conn.commit()
        status = "SUCCESS" if failed == 0 else "PARTIAL"
        log_validation(os.path.basename(filepath), processed, failed, status)
        print(f"Loaded {processed} new records from GFW file '{os.path.basename(filepath)}' (Failed/Skipped: {failed}).")
    except Exception as e:
        print(f"Failed processing GFW file {filepath}: {e}")
        log_validation(os.path.basename(filepath), 0, 0, "FAILED")

if __name__ == "__main__":
    run_etl()