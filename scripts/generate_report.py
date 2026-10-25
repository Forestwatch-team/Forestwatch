import os
import json
import psycopg
from dotenv import load_dotenv

load_dotenv()

DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "forestwatch")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD")

CONN_STR = f"host={DB_HOST} port={DB_PORT} dbname={DB_NAME} user={DB_USER} password={DB_PASSWORD}"

def generate_report():
    os.makedirs("reports", exist_ok=True)
    
    with psycopg.connect(CONN_STR) as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT COUNT(*) FROM forest_loss;")
            forest_count = cur.fetchone()[0]
            
            cur.execute("SELECT COUNT(*) FROM fire_alerts;")
            fire_count = cur.fetchone()[0]
            
            cur.execute("""
                SELECT source_file, SUM(records_processed) as total_processed, 
                       SUM(records_failed) as total_failed, status 
                FROM validation_logs 
                GROUP BY source_file, status;
            """)
            log_rows = cur.fetchall()
    
    report_data = {
        "database_summary": {
            "total_forest_loss_records": forest_count,
            "total_fire_alerts_records": fire_count
        },
        "ingestion_logs": [
            {
                "source_file": row[0],
                "records_processed": row[1],
                "records_failed": row[2],
                "status": row[3]
            }
            for row in log_rows
        ]
    }
    
    report_file = os.path.join("reports", "etl_summary_report.json")
    with open(report_file, "w") as f:
        json.dump(report_data, f, indent=4)
        
    print(f"Validation summary report generated successfully at '{report_file}'.")

if __name__ == "__main__":
    generate_report()