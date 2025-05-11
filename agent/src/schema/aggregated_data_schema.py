from marshmallow import Schema, fields
from schema.accelerometer_schema import AccelerometerSchema
from schema.gps_schema import GpsSchema


class AggregatedDataSchema(Schema):
    user_id = fields.Integer()
    accelerometer = fields.Nested(AccelerometerSchema)
    gps = fields.Nested(GpsSchema)
    timestamp = fields.DateTime('iso')
