# tests/test_api.py
import os
import sys
import pytest

# 1. Ensure project root is on sys.path so we can import run.py and app modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# 2. Override DB_URL *before* importing anything that creates an engine
os.environ["DB_URL"] = "sqlite:///:memory:"

from run import app
from app.models import Base, engine

@pytest.fixture(autouse=True)
def setup_db():
    """
    Automatically run for every test:
    - drop all tables (in-memory)
    - create all tables
    """
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

@pytest.fixture
def client():
    app.config["TESTING"] = True
    return app.test_client()

def test_weather_empty(client):
    """GET /api/weather/ returns [] on empty DB."""
    resp = client.get("/api/weather/", follow_redirects=True)
    assert resp.status_code == 200
    assert resp.is_json
    assert resp.get_json() == []

def test_weather_stats_empty(client):
    """GET /api/weather/stats/ returns [] on empty DB."""
    resp = client.get("/api/weather/stats/", follow_redirects=True)
    assert resp.status_code == 200
    assert resp.is_json
    assert resp.get_json() == []

def test_yield_empty(client):
    """GET /api/yield/ returns [] on empty DB."""
    resp = client.get("/api/yield/", follow_redirects=True)
    assert resp.status_code == 200
    assert resp.is_json
    assert resp.get_json() == []

def test_yield_stats_empty(client):
    """GET /api/yield/stats/ returns [] on empty DB."""
    resp = client.get("/api/yield/stats/", follow_redirects=True)
    assert resp.status_code == 200
    assert resp.is_json
    assert resp.get_json() == []
