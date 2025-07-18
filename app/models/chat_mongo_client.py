import datetime
import logging
import os
import asyncio

from pymongo.asynchronous.mongo_client import AsyncMongoClient
from pymongo.errors import DuplicateKeyError

from app.models.chat_models import ChatModel, MessageModel


class ChatsMongoClient:
    def __init__(self):
        self.client = AsyncMongoClient(os.environ.get("MONGODB_URL"))
        self.db = self.client[os.environ.get("MONGODB_DB_NAME")]
        self.collection = self.db['chats']
        self.logger = logging.getLogger('uvicorn.error')

    @staticmethod
    async def get_db():
        db = ChatsMongoClient()
        return db

    async def create_chat(self):
        chat = ChatModel()
        try:
            await self.collection.insert_one(chat.model_dump())
            return chat
        # Шанс коллизий крайне мал... но не нулевой
        except DuplicateKeyError:
            return await self.create_chat()

    async def get_chat(self, chat_id: str) -> ChatModel:
        chat = await self.collection.find_one({"chat_id": chat_id})
        return ChatModel.model_validate(chat)


    async def add_or_update_chat(self, chat: ChatModel):
        chat_id = chat.chat_id
        chat.last_update_timestamp = datetime.datetime.now()
        await self.collection.update_one(
            {'chat_id': chat_id}, {"$set": chat}, upsert=True)


    async def add_message(self, chat_id: str, message: str, sender_id: str, sender_type: str):
        self.logger.info(f"Adding message: {message} in chat: {chat_id} with sender_id: {sender_id}")
        chat = await self.get_chat(chat_id)
        self.logger.info(f"{chat}")
        chat.last_update_timestamp = datetime.datetime.now()
        if sender_id not in chat.participants:
            chat.participants[sender_id] = sender_type
        chat.messages.append(MessageModel(sender_id=sender_id, content=message))
        await self.collection.update_one(
            {'chat_id': chat_id}, {"$set": chat.model_dump()}, upsert=True)



