from marshmallow import Schema, fields


class PointCoordAttrsSchema(Schema):
    lat = fields.Float()
    lon = fields.Float()


class PointCoordSchema(Schema):
    point_coord = fields.Nested(PointCoordAttrsSchema())
