from tortoise import Model, fields


class User(Model):
    id = fields.IntField(pk=True)
    max_id = fields.IntField(unique=True)
    username = fields.CharField(max_length=255, unique=True, null=True)
    first_name = fields.CharField(max_length=255)
    last_name = fields.CharField(max_length=255, null=True)
    created_at = fields.DatetimeField(auto_now_add=True)
