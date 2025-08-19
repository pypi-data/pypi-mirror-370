import uuid
from datetime import datetime

from peewee import Model, CharField, IntegerField, TextField, DateTimeField

from ..configuration import DATABASE


class ApiUser(Model):
    uid = CharField(unique=True)

    name = CharField(unique=True)
    city = IntegerField()
    postal_code = CharField()

    class Meta:
        database = DATABASE
        table_name = "api_user"


class Message(Model):
    uid = CharField(unique=True, default=lambda: f"{uuid.uuid4().hex}")

    user_id = CharField()
    content = TextField()
    timestamp = DateTimeField(default=datetime.now)

    class Meta:
        database = DATABASE
        table_name = "messages"


class UserConf(Model):
    uid = CharField(unique=True, default=lambda: f"{uuid.uuid4().hex}")

    user_id = CharField(unique=True)
    user_name = CharField()
    json = CharField()
    last_update = DateTimeField(default=datetime.now)

    class Meta:
        database = DATABASE
        table_name = 'user_conf'
