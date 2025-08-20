from tortoise import Model, fields
from shared_models.enums import ModeratorType, ModerationResult
from .message import Message


class ModerationLog(Model):
    id = fields.IntField(pk=True)
    message: fields.ForeignKeyRelation[Message] = fields.ForeignKeyField(
        "models.Message",
        related_name="moderation_logs",
        on_delete=fields.CASCADE,
    )
    source = fields.CharEnumField(ModeratorType)
    result = fields.CharEnumField(ModerationResult)
    reason = fields.TextField(null=True)
    created_at = fields.DatetimeField(auto_now_add=True)
