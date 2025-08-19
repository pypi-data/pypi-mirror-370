from marshmallow import Schema, fields


class WorkflowAttrsSchema(Schema):
    name = fields.Str()
    part_id = fields.Int()


class WorkflowSchema(Schema):
    workflow = fields.Nested(WorkflowAttrsSchema())
