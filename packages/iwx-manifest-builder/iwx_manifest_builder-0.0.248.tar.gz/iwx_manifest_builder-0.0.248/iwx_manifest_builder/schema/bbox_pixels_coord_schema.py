from marshmallow import Schema, fields


class BboxPixelsCoordAttrsSchema(Schema):
    min_x = fields.Int()
    max_x = fields.Int()
    min_y = fields.Int()
    max_y = fields.Int()


class BboxPixelsCoordSchema(Schema):
    bbox_pixels_coord = fields.Nested(BboxPixelsCoordAttrsSchema())
    bbox_pixels_coord_area = fields.Int()
