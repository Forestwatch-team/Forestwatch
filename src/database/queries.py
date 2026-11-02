"""Read-only queries for the dashboard.

Every query function returns a pandas DataFrame.
load_meta_bundle() returns a dictionary of DataFrames.
"""

import pandas as pd

from src.database import db


def _df(sql, params=None) -> pd.DataFrame:
    with db.get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(sql, params)
            cols = [d.name for d in cur.description]
            rows = cur.fetchall()

    return pd.DataFrame(rows, columns=cols)


def table_counts() -> pd.DataFrame:
    return _df("""
        SELECT 'fire_alerts' AS table_name, COUNT(*) AS row_count
        FROM fire_alerts

        UNION ALL

        SELECT 'forest_loss', COUNT(*)
        FROM forest_loss

        UNION ALL

        SELECT 'validation_logs', COUNT(*)
        FROM validation_logs
    """)


def fire_date_range() -> pd.DataFrame:
    return _df("""
        SELECT MIN(acq_date) AS min_day, MAX(acq_date) AS max_day
        FROM fire_alerts
    """)


def fire_confidence_values() -> pd.DataFrame:
    return _df("""
        SELECT DISTINCT confidence
        FROM fire_alerts
        WHERE confidence IS NOT NULL
        ORDER BY confidence
    """)

def fire_daily_counts(start, end, classes) -> pd.DataFrame:
    df = _df("""
        SELECT acq_date AS alert_date, COUNT(*) AS detections
        FROM (
            SELECT DISTINCT latitude, longitude, acq_date, acq_time
            FROM fire_alerts
            WHERE acq_date BETWEEN %s AND %s
              AND (confidence = ANY(%s) OR confidence IS NULL)
        ) d
        GROUP BY acq_date ORDER BY acq_date
    """, (start, end, list(classes)))
    df["alert_date"] = pd.to_datetime(df["alert_date"])
    return df


def fire_points(start, end, classes, limit=20000) -> pd.DataFrame:
    return _df("""
        SELECT latitude::float8 AS latitude, longitude::float8 AS longitude,
               confidence, acq_date AS alert_date
        FROM (
            SELECT DISTINCT ON (latitude, longitude, acq_date, acq_time)
                   latitude, longitude, confidence, acq_date, acq_time
            FROM fire_alerts
            WHERE acq_date BETWEEN %s AND %s
              AND (confidence = ANY(%s) OR confidence IS NULL)
            ORDER BY latitude, longitude, acq_date, acq_time
        ) d
        ORDER BY acq_date DESC LIMIT %s
    """, (start, end, list(classes), limit))


def loss_countries() -> pd.DataFrame:
    return _df("""
        SELECT DISTINCT country
        FROM forest_loss
        WHERE country IS NOT NULL
        ORDER BY country
    """)


def loss_by_year(country) -> pd.DataFrame:
    return _df("""
        SELECT year, SUM(area_ha)::float8 AS area_ha
        FROM forest_loss
        WHERE country = %s
        GROUP BY year
        ORDER BY year
    """, (country,))


def quality_summary() -> pd.DataFrame:
    return _df("""
        SELECT created_at,
               source_file,
               records_processed,
               records_failed,
               status
        FROM validation_logs
        ORDER BY created_at DESC
        LIMIT 50
    """)

def load_meta_bundle() -> dict:
    sqls = {
        "counts": """SELECT 'fire_alerts' AS table_name, COUNT(*) AS row_count
                     FROM (SELECT DISTINCT latitude, longitude, acq_date, acq_time FROM fire_alerts) d
                     UNION ALL SELECT 'forest_loss', COUNT(*) FROM forest_loss
                     UNION ALL SELECT 'validation_logs', COUNT(*) FROM validation_logs""",
        "range": "SELECT MIN(acq_date) AS min_day, MAX(acq_date) AS max_day FROM fire_alerts",
        "classes": """SELECT DISTINCT confidence FROM fire_alerts
                      WHERE confidence IS NOT NULL ORDER BY confidence""",
        "countries": """SELECT DISTINCT country FROM forest_loss
                        WHERE country IS NOT NULL ORDER BY country""",
        "quality": """SELECT created_at, source_file, records_processed, records_failed, status
                      FROM validation_logs ORDER BY created_at DESC LIMIT 50""",
    }
    out = {}
    with db.get_connection() as conn:
        with conn.cursor() as cur:
            for key, sql in sqls.items():
                cur.execute(sql)
                cols = [d.name for d in cur.description]
                out[key] = pd.DataFrame(cur.fetchall(), columns=cols)
    return out