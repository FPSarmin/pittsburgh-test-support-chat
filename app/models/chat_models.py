import datetime
from typing import List, Dict, Optional

from pydantic import BaseModel, Field
from random_object_id import generate

class MessageModel(BaseModel):
    sender_id: str = Field(alias="sender_id")
    content: str = Field(alias="content")

class ChatModel(BaseModel):
    chat_id: str = Field(default_factory=generate)
    messages: List[MessageModel] = Field(default_factory=lambda: [])
    participants: Dict = Field(default_factory=lambda: {})
    last_update_timestamp: datetime.datetime = Field(default_factory=datetime.datetime.now)

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True

class ChatModelForApiRequest(BaseModel):
    type: str = Field(default="message", alias="type")
    sender_id: str = Field(alias="sender_id")
    content: str = Field(alias="content")


class CreatedChatIdModel(BaseModel):
    chat_id: str = Field(alias="chat_id")

