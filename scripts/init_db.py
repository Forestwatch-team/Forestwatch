import os
import psycopg
from dotenv import load_dotenv

# Load credentials from .env
load_dotenv()

DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "forestwatch")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "forestwatchadmin3@@@")

def init_db():
    schema_path = os.path.join("sql", "schema.sql")
    if not os.path.exists(schema_path):
        print(f"Error: {schema_path} not found. Please create sql/schema.sql first.")
        return

    conn_str = f"host={DB_HOST} port={DB_PORT} dbname={DB_NAME} user={DB_USER} password={DB_PASSWORD}"

    try:
        with open(schema_path, "r") as f:
            sql_script = f.read()

        with psycopg.connect(conn_str) as conn:
            with conn.cursor() as cur:
                cur.execute(sql_script)
            conn.commit()
        print("Database schema created successfully!")
    except Exception as e:
        print(f"Database error: {e}")

if __name__ == "__main__":
    init_db()