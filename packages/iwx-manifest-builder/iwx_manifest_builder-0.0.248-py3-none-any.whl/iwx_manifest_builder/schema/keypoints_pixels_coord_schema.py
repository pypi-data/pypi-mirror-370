from marshmallow import Schema, fields


class KeypointSinglePointPixelsCoordAttrsSchema(Schema):
    x = fields.Int()
    y = fields.Int()
    score = fields.Float()


class KeypointsPixelsCoordAttrsSchema(Schema):
    shadow_base = fields.Nested(KeypointSinglePointPixelsCoordAttrsSchema())
    shadow_end = fields.Nested(KeypointSinglePointPixelsCoordAttrsSchema())


class KeypointsPixelsCoordSchema(Schema):
    keypoints = fields.Nested(KeypointsPixelsCoordAttrsSchema())
