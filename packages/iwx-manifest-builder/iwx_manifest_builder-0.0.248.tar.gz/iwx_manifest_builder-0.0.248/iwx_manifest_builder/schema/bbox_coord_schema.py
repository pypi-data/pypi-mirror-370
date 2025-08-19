from marshmallow import Schema, fields


class BboxCoordAttrsSchema(Schema):
    min_lat = fields.Float()
    max_lat = fields.Float()
    min_lon = fields.Float()
    max_lon = fields.Float()


class BboxCoordSchema(Schema):
    bbox_coord = fields.Nested(BboxCoordAttrsSchema())
