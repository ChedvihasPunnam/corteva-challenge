from flask_smorest import Blueprint
from flask import request
from app.models import SessionLocal, YieldRecord
from app.schemas import YieldRecordSchema

blp = Blueprint(
    "yield_records", "yield_records",
    url_prefix="/api/yield",
    description="Crop yield records"
)


@blp.route("/")
@blp.response(200, YieldRecordSchema(many=True))
def get_yield():
    session = SessionLocal()
    q = session.query(YieldRecord)

    if sid := request.args.get("station_id"):
        q = q.filter(YieldRecord.station_id == sid)
    if yf := request.args.get("year_from", type=int):
        q = q.filter(YieldRecord.year >= yf)
    if yt := request.args.get("year_to", type=int):
        q = q.filter(YieldRecord.year <= yt)

    page     = int(request.args.get("page", 1))
    per_page = int(request.args.get("per_page", 100))
    results  = q.offset((page - 1) * per_page).limit(per_page).all()

    session.close()
    return results
