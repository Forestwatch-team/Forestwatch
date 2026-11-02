import pytest

from src import config
from src.database import db


def test_unreachable_database_raises_friendly_error(monkeypatch):
    monkeypatch.setattr(config, "DATABASE_URL", "postgresql://u:p@127.0.0.1:1/none")
    with pytest.raises(db.DatabaseUnavailable):
        with db.get_connection():
            pass


def test_missing_database_url_is_reported(monkeypatch):
    monkeypatch.setattr(config, "DATABASE_URL", "")
    with pytest.raises(RuntimeError):
        with db.get_connection():
            pass