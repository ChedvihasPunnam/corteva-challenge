"""Unit tests for weather statistics analysis logic."""

import os
import sys
from datetime import date

import pytest

# 1. Ensure project root is on sys.path so we can import app modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# 2. Point DB_URL at in-memory SQLite before importing anything
os.environ["DB_URL"] = "sqlite:///:memory:"

from app.analysis import compute_and_store_stats
from app.models import Base, SessionLocal, WeatherRecord, WeatherStats, engine


@pytest.fixture(autouse=True)
def init_db():
    """Pytest fixture to create and drop all tables for each test."""
    # create tables
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


def test_compute_stats_basic():
    """Test that compute_and_store_stats correctly aggregates valid weather data."""
    session = SessionLocal()

    # Station "S1" in year 2000: two valid days and one missing day
    records = [
        {
            "station_id": "S1",
            "obs_date": date(2000, 1, 1),
            "tmax_c_tenths": 200,
            "tmin_c_tenths": 50,
            "precip_mm_tenths": 100,
        },
        {
            "station_id": "S1",
            "obs_date": date(2000, 1, 2),
            "tmax_c_tenths": 300,
            "tmin_c_tenths": 150,
            "precip_mm_tenths": 200,
        },
        # missing values on this date; should be ignored
        {
            "station_id": "S1",
            "obs_date": date(2000, 1, 3),
            "tmax_c_tenths": -9999,
            "tmin_c_tenths": -9999,
            "precip_mm_tenths": -9999,
        },
    ]
    for rec in records:
        session.add(WeatherRecord(**rec))
    session.commit()
    session.close()

    # Run analysis
    compute_and_store_stats()

    # Verify stats
    session = SessionLocal()
    stat = session.query(WeatherStats).filter_by(station_id="S1", year=2000).one()
    # avg_tmax_c = (200/10 + 300/10)/2 = (20 + 30)/2 = 25.0
    assert pytest.approx(stat.avg_tmax_c, rel=1e-3) == 25.0
    # avg_tmin_c = (50/10 + 150/10)/2 = (5 + 15)/2 = 10.0
    assert pytest.approx(stat.avg_tmin_c, rel=1e-3) == 10.0
    # total_precip_cm = (100/100 + 200/100) = 1.0 + 2.0 = 3.0
    assert pytest.approx(stat.total_precip_cm, rel=1e-3) == 3.0

    session.close()


def test_stats_all_missing():
    """Test that compute_and_store_stats handles all-missing data for a station/year."""
    session = SessionLocal()

    # Station "S2" only missing data in 2001
    records = [
        {
            "station_id": "S2",
            "obs_date": date(2001, 5, 1),
            "tmax_c_tenths": -9999,
            "tmin_c_tenths": -9999,
            "precip_mm_tenths": -9999,
        },
        {
            "station_id": "S2",
            "obs_date": date(2001, 6, 1),
            "tmax_c_tenths": -9999,
            "tmin_c_tenths": -9999,
            "precip_mm_tenths": -9999,
        },
    ]
    for rec in records:
        session.add(WeatherRecord(**rec))
    session.commit()
    session.close()

    # Run analysis
    compute_and_store_stats()

    # Verify no stats row created for all-missing data
    session = SessionLocal()
    stat = session.query(WeatherStats).filter_by(station_id="S2", year=2001).first()
    assert stat is None
    session.close()
