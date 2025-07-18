from fastapi import APIRouter, HTTPException

from app.models.chat_models import CreatedChatIdModel
from app.models.chat_mongo_client import ChatsMongoClient, chats_mongo_client

chat_router = APIRouter()

@chat_router.post("/chats", response_model=CreatedChatIdModel)
async def create_chat_endpoint():
    try:
        return await chats_mongo_client.create_chat()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@chat_router.get("/chats/{chat_id}/messages")
async def create_chat_endpoint(chat_id: str):
    try:
        chat = await chats_mongo_client.get_chat(chat_id)
        return chat.messages
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

