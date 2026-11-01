"""Settings come from the environment (.env on your computer). Nothing is hardcoded."""
import os
from pathlib import Path
from urllib.parse import quote_plus

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")


def _build_database_url() -> str:
    direct = os.getenv("DATABASE_URL", "")
    if direct:
        return direct
    host = os.getenv("DB_HOST")
    user = os.getenv("DB_USER")
    if not host or not user:
        return ""
    pw = quote_plus(os.getenv("DB_PASSWORD", ""))
    port = os.getenv("DB_PORT", "6543")
    name = os.getenv("DB_NAME", "postgres")
    return f"postgresql://{quote_plus(user)}:{pw}@{host}:{port}/{name}?sslmode=require"


DATABASE_URL = _build_database_url()