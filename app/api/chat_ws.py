import datetime
import json
import logging

from fastapi import APIRouter, Query
from starlette.responses import JSONResponse
from starlette.websockets import WebSocket, WebSocketDisconnect

from app.connection_manager.connection_manager import ConnectionManager
from app.models.chat_models import ChatModelForApiRequest
from app.models.chat_mongo_client import chats_mongo_client

chat_ws_router = APIRouter()
connectionManager = ConnectionManager()


@chat_ws_router.websocket("/ws/{chat_id}")
async def websocket_endpoint(
        websocket: WebSocket,
        chat_id: str,
        user_type: str = Query(...),
        user_id: str = Query(...)
):
    logger = logging.getLogger('uvicorn.error')
    chat = await chats_mongo_client.get_chat(chat_id)
    if chat is None:
        return JSONResponse(
            status_code=400,
            content={"message": "Ошибка запроса", "detail": "Не существует чата с данным chat_id"},
        )
    curr_user_type = user_type
    await chats_mongo_client.add_participant(chat_id, user_id, curr_user_type)
    await connectionManager.connect(websocket, chat_id, user_id)
    try:
        while True:
            json_data = await websocket.receive_json()
            logger.info(f"Received message: {json_data}")
            data = ChatModelForApiRequest.model_validate(json_data)
            message_data = {
                "type": "message",
                "sender_id": user_id,
                "sender_type": curr_user_type,
                "content": data.content
            }
            logger.info(f'Sent message: {json.dumps(message_data, default=str)}')

            await chats_mongo_client.add_message(chat_id, data.content, data.sender_id, user_type)
            # Рассылаем всем участникам чата кроме отправляющего
            await connectionManager.broadcast(message_data, chat_id, user_id)

    except WebSocketDisconnect:
        connectionManager.disconnect(chat_id, user_id)
        await connectionManager.broadcast({
            "type": "system",
            "content": f"User {user_id} disconnected",
            "timestamp": datetime.datetime.now(),
            "user_id": user_id
        }, chat_id)
    except json.JSONDecodeError:
        await websocket.send_json({
            "type": "error",
            "content": "Invalid JSON format"
        })