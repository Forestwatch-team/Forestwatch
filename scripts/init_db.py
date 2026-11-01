import os
import psycopg
from dotenv import load_dotenv

# Find the absolute path to the root folder where .env is located
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
dotenv_path = os.path.join(BASE_DIR, '.env')

# Load credentials from .env safely using the absolute path
load_dotenv(dotenv_path=dotenv_path)

DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT", "6543")  # Defaults to 6543 if not specified
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")

def init_db():
    # Make sure schema_path is absolute so it doesn't break from subfolders
    schema_path = os.path.join(BASE_DIR, "sql", "schema.sql")
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
