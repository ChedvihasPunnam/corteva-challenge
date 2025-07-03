"""Analysis logic for computing yearly weather statistics from daily records."""
import logging
from datetime import datetime

from sqlalchemy import case, extract, func

from app.models import Base, SessionLocal, WeatherRecord, WeatherStats, engine

# configure logging
logging.basicConfig(format="%(asctime)s %(levelname)s:%(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)


def compute_and_store_stats():
    """Compute yearly weather statistics and store them in the database."""
    session = SessionLocal()

    # ensure table exists
    Base.metadata.create_all(bind=engine, tables=[WeatherStats.__table__])
    logger.info("Ensured weather_stats table exists")

    # define NULL-aware conversions
    tmax_c = case(
        (WeatherRecord.tmax_c_tenths != -9999, WeatherRecord.tmax_c_tenths / 10.0),
        else_=None,
    )
    tmin_c = case(
        (WeatherRecord.tmin_c_tenths != -9999, WeatherRecord.tmin_c_tenths / 10.0),
        else_=None,
    )
    precip_cm = case(
        (
            WeatherRecord.precip_mm_tenths != -9999,
            WeatherRecord.precip_mm_tenths / 100.0,
        ),
        else_=None,
    )

    # aggregate per station/year
    stats_query = session.query(
        WeatherRecord.station_id,
        extract("year", WeatherRecord.obs_date).label("year"),
        func.avg(tmax_c).label("avg_tmax_c"),
        func.avg(tmin_c).label("avg_tmin_c"),
        func.sum(precip_cm).label("total_precip_cm"),
    ).group_by(WeatherRecord.station_id, "year")

    # upsert into stats table
    for station_id, year, avg_max, avg_min, total_prec in stats_query:
        session.merge(
            WeatherStats(
                station_id=station_id,
                year=int(year),
                avg_tmax_c=avg_max,
                avg_tmin_c=avg_min,
                total_precip_cm=total_prec,
            )
        )

    session.commit()
    session.close()


if __name__ == "__main__":
    start = datetime.utcnow()
    logger.info(f"Analysis started at {start.isoformat()}")
    compute_and_store_stats()
    end = datetime.utcnow()
    logger.info(
        f"Analysis finished at {end.isoformat()} "
        f"— elapsed {(end-start).total_seconds():.2f}s"
    )
