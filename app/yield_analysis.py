import logging
from datetime import datetime

from sqlalchemy import func, case

from app.models import Base, engine, SessionLocal, YieldRecord, YieldStats

# configure logging
logging.basicConfig(
    format="%(asctime)s %(levelname)s:%(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

def compute_and_store_yield_stats():
    session = SessionLocal()

    # ensure table exists
    Base.metadata.create_all(bind=engine, tables=[YieldStats.__table__])
    logger.info("Ensured yield_stats table exists")

    # convert -9999 → NULL and tenths → units
    yield_bu = case(
        (YieldRecord.yield_bu_tenths != -9999, YieldRecord.yield_bu_tenths / 10.0),
        else_=None
    )

    # aggregate per station/year
    stats_q = (
        session.query(
            YieldRecord.station_id,
            YieldRecord.year.label("year"),
            func.avg(yield_bu).label("avg_yield_bu")
        )
        .group_by(YieldRecord.station_id, YieldRecord.year)
    )

    # upsert into yield_stats
    for station_id, year, avg_yield in stats_q:
        session.merge(
            YieldStats(
                station_id=station_id,
                year=year,
                avg_yield_bu=avg_yield
            )
        )

    session.commit()
    session.close()

if __name__ == "__main__":
    start = datetime.utcnow()
    logger.info(f"Yield analysis started at {start.isoformat()}")
    compute_and_store_yield_stats()
    end = datetime.utcnow()
    logger.info(f"Yield analysis finished at {end.isoformat()} — elapsed {(end-start).total_seconds():.2f}s")
