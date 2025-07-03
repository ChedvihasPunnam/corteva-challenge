import glob
import os
import io
import psycopg2
import logging
from datetime import datetime

from app.models import Base, engine, Station

# configure logging
logging.basicConfig(
    format="%(asctime)s %(levelname)s:%(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

DB_URL = os.getenv("DB_URL", "postgresql://user:pass@db:5432/weatherdb")

def ingest_with_copy():
    # 0) Ensure all tables exist (stations, weather_records, yield_records)
    Base.metadata.create_all(bind=engine)
    logger.info("Ensured all tables exist")

    conn = psycopg2.connect(DB_URL)
    cur  = conn.cursor()

    #
    # ─── WEATHER INGESTION ────────────────────────────────────────────────────────
    #
    # 1a) Truncate old weather data
    cur.execute("TRUNCATE TABLE weather_records;")
    logger.info("Truncated weather_records")

    total_wx = 0
    for path in glob.glob("/app/wx_data/*.txt"):
        station = os.path.splitext(os.path.basename(path))[0]

        # 1b) Upsert station row
        cur.execute(
            "INSERT INTO stations (station_id, state) VALUES (%s, %s) "
            "ON CONFLICT (station_id) DO NOTHING;",
            (station, station[:2])
        )

        # 1c) Load weather file
        with open(path, "r") as f:
            lines = f.readlines()
        count = len(lines)
        total_wx += count

        data = "".join(f"{station}\t{line}" for line in lines)
        buf  = io.StringIO(data)
        cur.copy_expert(
            """
            COPY weather_records
              (station_id, obs_date, tmax_c_tenths, tmin_c_tenths, precip_mm_tenths)
            FROM STDIN
            WITH (FORMAT csv, DELIMITER E'\t', HEADER FALSE)
            """,
            buf
        )
        logger.info(f"[Weather] loaded {count} rows from {os.path.basename(path)}")

    # 1d) Verify weather total
    cur.execute("SELECT COUNT(*) FROM weather_records;")
    wx_count = cur.fetchone()[0]
    logger.info(f"[Weather] total records: {wx_count} (expected ~{total_wx})")

    #
    # ─── YIELD INGESTION ──────────────────────────────────────────────────────────
    #
    # 2a) Truncate old yield data
    cur.execute("TRUNCATE TABLE yield_records;")
    logger.info("Truncated yield_records")

    total_yd = 0
    for path in glob.glob("/app/yld_data/*.txt"):
        station = os.path.splitext(os.path.basename(path))[0]

        # 2b) Upsert station row (if not already)
        cur.execute(
            "INSERT INTO stations (station_id, state) VALUES (%s, %s) "
            "ON CONFLICT (station_id) DO NOTHING;",
            (station, station[:2])
        )

        # 2c) Load yield file
        with open(path, "r") as f:
            lines = f.readlines()
        count = len(lines)
        total_yd += count

        data = "".join(f"{station}\t{line}" for line in lines)
        buf  = io.StringIO(data)
        cur.copy_expert(
            """
            COPY yield_records
              (station_id, year, yield_bu_tenths)
            FROM STDIN
            WITH (FORMAT csv, DELIMITER E'\t', HEADER FALSE)
            """,
            buf
        )
        logger.info(f"[Yield]   loaded {count} rows from {os.path.basename(path)}")

    # 2d) Verify yield total
    cur.execute("SELECT COUNT(*) FROM yield_records;")
    yd_count = cur.fetchone()[0]
    logger.info(f"[Yield] total records: {yd_count} (expected ~{total_yd})")

    conn.commit()
    cur.close()
    conn.close()

if __name__ == "__main__":
    start = datetime.utcnow()
    logger.info(f"Bulk ingestion starting at {start.isoformat()}")
    ingest_with_copy()
    end = datetime.utcnow()
    logger.info(f"Bulk ingestion finished at {end.isoformat()} — elapsed {(end-start).total_seconds():.2f}s")
