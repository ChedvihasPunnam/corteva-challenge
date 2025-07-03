# app/routes/yield_stats.py

from flask_smorest import Blueprint
from flask import request
from app.models import SessionLocal, YieldStats
from app.schemas import YieldStatsSchema

blp = Blueprint(
    "yield_stats", "yield_stats",
    url_prefix="/api/yield/stats",
    description="Per‐station yearly crop yield statistics"
)

@blp.route("/")
@blp.response(200, YieldStatsSchema(many=True))
def get_yield_stats():
    session = SessionLocal()
    q = session.query(YieldStats)

    if sid := request.args.get("station_id"):
        q = q.filter(YieldStats.station_id == sid)
    if yf := request.args.get("year_from", type=int):
        q = q.filter(YieldStats.year >= yf)
    if yt := request.args.get("year_to",   type=int):
        q = q.filter(YieldStats.year <= yt)

    page     = int(request.args.get("page", 1))
    per_page = int(request.args.get("per_page", 100))
    results  = q.offset((page - 1) * per_page).limit(per_page).all()

    session.close()
    return results
