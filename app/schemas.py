from marshmallow import Schema, fields

class WeatherRecordSchema(Schema):
    station_id       = fields.Str(required=True)
    obs_date         = fields.Date(required=True)
    tmax_c_tenths    = fields.Int(required=True)
    tmin_c_tenths    = fields.Int(required=True)
    precip_mm_tenths = fields.Int(required=True)

class WeatherStatsSchema(Schema):
    station_id      = fields.Str(required=True)
    year            = fields.Int(required=True)
    avg_tmax_c      = fields.Float(allow_none=True)
    avg_tmin_c      = fields.Float(allow_none=True)
    total_precip_cm = fields.Float(allow_none=True)

class YieldRecordSchema(Schema):
    station_id      = fields.Str(required=True)
    year            = fields.Int(required=True)
    yield_bu_tenths = fields.Int(required=True)

class YieldStatsSchema(Schema):
    station_id    = fields.Str(required=True)
    year          = fields.Int(required=True)
    avg_yield_bu  = fields.Float(allow_none=True)
