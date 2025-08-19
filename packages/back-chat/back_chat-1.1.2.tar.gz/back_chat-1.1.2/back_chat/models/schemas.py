import datetime
import json

from pydantic import BaseModel, validator

from ..descriptors import MessageMode, MessageType


class UserSchema(BaseModel):
    name: str = ''
    postal_code: str = ''
    city: str = '-'

    class Config:
        orm_mode = True
        from_attributes = True


class ShowUserSchema(BaseModel):
    id: str = 0
    name: str = ''
    postal_code: str = ''
    city: str = '-'

    class Config:
        orm_mode = True
        from_attributes = True


class UserConnection(BaseModel):
    name: str
    status: str = 'online'
    lastConnection: datetime.datetime or str = datetime.datetime.now()

    class Config:
        from_attributes = True


class MessageSchema(BaseModel):
    user_id: str
    content: str = ''
    timestamp: datetime.datetime or str = datetime.datetime.now()
    mtype: str = MessageType.MESSAGE.value
    isMine: bool = False

    class Config:
        __type_descriptor__ = MessageMode()
        orm_mode = True
        from_attributes = True

    @validator('mtype')
    def validate_mode(cls, v):
        if isinstance(v, MessageType):
            v = v.value
        cls.Config.__type_descriptor__ = v
        return v

    def connection_msg(self):
        self.mtype = MessageType.CONNECT.value
        self.content = "join the chat"

    def disconnection_msg(self):
        self.mtype = MessageType.DISCONNECT.value
        self.content = "left the chat"

    def to_json(self):
        if self.user_id.isdigit():
            self.user_id = f'Client {self.user_id}'
        dict_ = dict(self)
        dict_['timestamp'] = str(dict_['timestamp'])
        return json.dumps(dict_)


class NotificationSchema(BaseModel):
    content: dict = {}
    timestamp: datetime.datetime or str = datetime.datetime.now()
    type: str = MessageType.MESSAGE.value

    class Config:
        __type_descriptor__ = MessageMode()
        from_attributes = True

    @validator('type')
    def validate_mode(cls, v):
        if isinstance(v, MessageType):
            v = v.value
        cls.Config.__type_descriptor__ = v
        return v

    def connection_msg(self):
        self.mtype = MessageType.CONNECT.value
        self.content = "join the chat"

    def disconnection_msg(self):
        self.mtype = MessageType.DISCONNECT.value
        self.content = "left the chat"

    def to_json(self):
        if self.user_id.isdigit():
            self.user_id = f'Client {self.user_id}'
        dict_ = dict(self)
        dict_['timestamp'] = str(dict_['timestamp'])
        return json.dumps(dict_)
