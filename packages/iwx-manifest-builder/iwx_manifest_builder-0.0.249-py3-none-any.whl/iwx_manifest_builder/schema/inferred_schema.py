from marshmallow import Schema, fields


class InferredAttrsSchema(Schema):
    best_lat = fields.Float()
    best_lon = fields.Float()
    adjusted_height = fields.Float()
    unadjusted_height = fields.Float()


class InferredSchema(Schema):
    inferred = fields.Nested(InferredAttrsSchema())
