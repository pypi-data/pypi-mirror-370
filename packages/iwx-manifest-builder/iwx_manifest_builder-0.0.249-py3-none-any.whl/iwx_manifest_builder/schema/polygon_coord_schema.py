from marshmallow import Schema, fields


class PolygonCoordSchema(Schema):
    polygon_coord = fields.List(fields.List(fields.Float(default=0)))
