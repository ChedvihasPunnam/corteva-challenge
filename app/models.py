import os

from sqlalchemy import (
    create_engine,
    Column,
    String,
    Date,
    SmallInteger,
    Integer,
    Float,
    ForeignKey,
)
from sqlalchemy.orm import sessionmaker, declarative_base

# Read DB_URL from env (fallback to localhost)
DB_URL = os.getenv(
    "DB_URL",
    "postgresql://user:pass@localhost:5432/weatherdb"
)

engine = create_engine(DB_URL)
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()


class Station(Base):
    __tablename__ = "stations"

    station_id = Column(String(20), primary_key=True, index=True)
    state      = Column(String(2),  nullable=False)
    name       = Column(String,      nullable=True)


class WeatherRecord(Base):
    __tablename__ = "weather_records"

    station_id       = Column(
        String(20),
        ForeignKey("stations.station_id", ondelete="CASCADE"),
        primary_key=True,
        index=True
    )
    obs_date         = Column(Date,         primary_key=True)
    tmax_c_tenths    = Column(SmallInteger, nullable=False)
    tmin_c_tenths    = Column(SmallInteger, nullable=False)
    precip_mm_tenths = Column(SmallInteger, nullable=False)


class WeatherStats(Base):
    __tablename__ = "weather_stats"

    station_id      = Column(String(20), primary_key=True)
    year            = Column(Integer,    primary_key=True)
    avg_tmax_c      = Column(Float, nullable=True)
    avg_tmin_c      = Column(Float, nullable=True)
    total_precip_cm = Column(Float, nullable=True)
