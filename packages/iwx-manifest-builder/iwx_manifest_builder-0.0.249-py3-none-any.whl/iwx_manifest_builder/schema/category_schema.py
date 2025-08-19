from marshmallow import Schema, fields


class CategoryAttrsSchema(Schema):
    id = fields.Int()
    enum = fields.Str()
    name = fields.Str()


class CategorySchema(Schema):
    category = fields.Nested(CategoryAttrsSchema())
