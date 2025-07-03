"""Marshmallow schemas for serializing weather data models."""

from marshmallow import Schema, fields


class WeatherRecordSchema(Schema):
    """Schema for serializing WeatherRecord model."""

    station_id = fields.Str(required=True)
    obs_date = fields.Date(required=True)
    tmax_c_tenths = fields.Int(required=True)
    tmin_c_tenths = fields.Int(required=True)
    precip_mm_tenths = fields.Int(required=True)


class WeatherStatsSchema(Schema):
    """Schema for serializing WeatherStats model."""

    station_id = fields.Str(required=True)
    year = fields.Int(required=True)
    avg_tmax_c = fields.Float(allow_none=True)
    avg_tmin_c = fields.Float(allow_none=True)
    total_precip_cm = fields.Float(allow_none=True)
