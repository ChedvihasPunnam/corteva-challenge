"""Data ingestion script for weather data."""

import glob
import io
import logging
import os
from datetime import datetime

import psycopg2

from app.models import Base, engine

# Configure logging for the ingestion process
logging.basicConfig(format="%(asctime)s %(levelname)s:%(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

DB_URL = os.getenv("DB_URL", "postgresql://user:pass@db:5432/weatherdb")


def ingest_with_copy():
    """Bulk-ingest weather data from /app/wx_data/*.txt into the database."""
    # Ensure all tables exist (stations, weather_records)
    Base.metadata.create_all(bind=engine)
    logger.info("Ensured all tables exist")

    conn = psycopg2.connect(DB_URL)
    cur = conn.cursor()

    # --- WEATHER INGESTION ---
    # Truncate old weather data
    cur.execute("TRUNCATE TABLE weather_records;")
    logger.info("Truncated weather_records")

    total_wx = 0
    for path in glob.glob("/app/wx_data/*.txt"):
        station = os.path.splitext(os.path.basename(path))[0]

        # Upsert station row (insert if not exists)
        cur.execute(
            "INSERT INTO stations (station_id, state) VALUES (%s, %s) "
            "ON CONFLICT (station_id) DO NOTHING;",
            (station, station[:2]),
        )

        # Load weather file and prepare data for COPY
        with open(path) as f:
            lines = f.readlines()
        count = len(lines)
        total_wx += count

        data = "".join(f"{station}\t{line}" for line in lines)
        buf = io.StringIO(data)
        cur.copy_expert(
            """
            COPY weather_records
              (station_id, obs_date, tmax_c_tenths, tmin_c_tenths, precip_mm_tenths)
            FROM STDIN
            WITH (FORMAT csv, DELIMITER E'\t', HEADER FALSE)
            """,
            buf,
        )
        logger.info(f"[Weather] loaded {count} rows from {os.path.basename(path)}")

    # Verify weather total
    cur.execute("SELECT COUNT(*) FROM weather_records;")
    wx_count = cur.fetchone()[0]
    logger.info(f"[Weather] total records: {wx_count} (expected ~{total_wx})")

    conn.commit()
    cur.close()
    conn.close()


if __name__ == "__main__":
    start = datetime.utcnow()
    logger.info(f"Bulk ingestion starting at {start.isoformat()}")
    ingest_with_copy()
    end = datetime.utcnow()
    logger.info(
        f"Bulk ingestion finished at {end.isoformat()} "
        f"— elapsed {(end-start).total_seconds():.2f}s"
    )
