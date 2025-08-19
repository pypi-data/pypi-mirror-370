from marshmallow import Schema, fields


class ImageAttrsSchema(Schema):
    name = fields.Str()
    width = fields.Int()
    height = fields.Int()
    resolution = fields.Float()


class ImageSchema(Schema):
    image = fields.Nested(ImageAttrsSchema())
