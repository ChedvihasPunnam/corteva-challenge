"""Unit tests for API endpoints in the weather data application."""
import os
import sys

import pytest

# 1. Ensure project root is on sys.path so we can import run.py and app modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# 2. Override DB_URL *before* importing anything that creates an engine
os.environ["DB_URL"] = "sqlite:///:memory:"

from app.models import Base, engine
from run import app


@pytest.fixture(autouse=True)
def setup_db():
    """Automatically run for every test.

    - Drop all tables (in-memory)
    - Create all tables
    """
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def client():
    """Return a Flask test client for the API."""
    app.config["TESTING"] = True
    return app.test_client()


def test_weather_empty(client):
    """Test that GET /api/weather/ returns [] on empty DB."""
    resp = client.get("/api/weather/", follow_redirects=True)
    assert resp.status_code == 200
    assert resp.is_json
    assert resp.get_json() == []


def test_weather_stats_empty(client):
    """Test that GET /api/weather/stats/ returns [] on empty DB."""
    resp = client.get("/api/weather/stats/", follow_redirects=True)
    assert resp.status_code == 200
    assert resp.is_json
    assert resp.get_json() == []
