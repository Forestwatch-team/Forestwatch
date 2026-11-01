"""Database connection with a friendly error when the database is unreachable."""
from contextlib import contextmanager

import psycopg

from src import config


class DatabaseUnavailable(Exception):
    """Raised when the database cannot be reached."""


@contextmanager
def get_connection():
    url = config.DATABASE_URL
    if not url:
        raise RuntimeError("Database settings are missing. Check your .env file.")
    try:
        # prepare_threshold=None: needed for the Supabase pooler (port 6543)
        conn = psycopg.connect(url, connect_timeout=10, prepare_threshold=None)
    except psycopg.Error as exc:
        raise DatabaseUnavailable("The database is not reachable.") from exc
    try:
        yield conn
    finally:
        conn.close()