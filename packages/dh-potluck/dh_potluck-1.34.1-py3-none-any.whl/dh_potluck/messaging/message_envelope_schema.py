from marshmallow import EXCLUDE, Schema, fields


class MessageEnvelopeSchema(Schema):
    message_type = fields.String(required=True)
    message_time = fields.DateTime(required=True)
    payload = fields.String(required=True)

    class Meta:
        unknown = EXCLUDE
