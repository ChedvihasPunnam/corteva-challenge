from flask_smorest import Blueprint
from flask import request
from app.models import SessionLocal, WeatherStats
from app.schemas import WeatherStatsSchema

blp = Blueprint("stats", __name__, url_prefix="/api/weather/stats", description="Yearly summary data")

@blp.route("/")
@blp.response(200, WeatherStatsSchema(many=True))
def get_stats():
    session = SessionLocal()
    q = session.query(WeatherStats)
    if yr := request.args.get("year", type=int):
        q = q.filter(WeatherStats.year == yr)
    if sid := request.args.get("station_id"):
        q = q.filter(WeatherStats.station_id == sid)
    page = int(request.args.get("page", 1))
    per_page = int(request.args.get("per_page", 100))
    results = q.offset((page - 1) * per_page).limit(per_page).all()
    session.close()
    return results
