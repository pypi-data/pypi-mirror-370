from tortoise import Model, fields
from .user import User
from shared_models.enums import MessageState


class Message(Model):
    id = fields.IntField(pk=True)
    user: fields.ForeignKeyRelation[User] = fields.ForeignKeyField(
        "models.User",
        related_name="messages",
        on_delete=fields.CASCADE,
    )
    text = fields.CharField(max_length=255)
    name = fields.CharField(max_length=255)
    city = fields.CharField(max_length=255)
    send_photo = fields.BooleanField()
    show_time_start = fields.DatetimeField(null=True)
    show_time_end = fields.DatetimeField(null=True)
    state = fields.CharEnumField(MessageState)
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)
