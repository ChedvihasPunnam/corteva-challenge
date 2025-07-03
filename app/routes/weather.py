"""API endpoints for accessing daily weather records."""
from flask import request
from flask_smorest import Blueprint

from app.models import SessionLocal, WeatherRecord
from app.schemas import WeatherRecordSchema

blp = Blueprint(
    "weather", __name__, url_prefix="/api/weather", description="Daily weather data"
)


@blp.route("/")
@blp.response(200, WeatherRecordSchema(many=True))
def get_weather():
    """Return paginated daily weather records, filtered by date or station."""
    session = SessionLocal()
    q = session.query(WeatherRecord)
    if df := request.args.get("date_from"):
        q = q.filter(WeatherRecord.obs_date >= df)
    if dt := request.args.get("date_to"):
        q = q.filter(WeatherRecord.obs_date <= dt)
    if sid := request.args.get("station_id"):
        q = q.filter(WeatherRecord.station_id == sid)
    page = int(request.args.get("page", 1))
    per_page = int(request.args.get("per_page", 100))
    results = q.offset((page - 1) * per_page).limit(per_page).all()
    session.close()
    return results
