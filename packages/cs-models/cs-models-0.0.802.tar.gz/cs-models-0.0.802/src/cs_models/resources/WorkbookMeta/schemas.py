from marshmallow import (
    Schema,
    fields,
)


class WorkbookMetaResourceSchema(Schema):
    workbook_id = fields.Integer(required=True)
    base_version = fields.Integer(required=True)
