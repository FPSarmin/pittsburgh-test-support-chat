import json
import logging
from typing import Dict

from starlette.websockets import WebSocket

from app.firebase.firebase_client import fb_client
from app.models.chat_models import ChatModel
from app.models.chat_mongo_client import chats_mongo_client


class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, Dict[str, WebSocket]] = {}
        self.logger = logging.getLogger('uvicorn.error')

    async def connect(self, websocket: WebSocket, chat_id: str, user_id: str):
        """
        Устанавливает соединение с пользователем.
        websocket.accept() — подтверждает подключение.
        """
        await websocket.accept()
        if chat_id not in self.active_connections:
            self.active_connections[chat_id] = {}
        self.active_connections[chat_id][user_id] = websocket

    def disconnect(self, chat_id: str, user_id: str):

        if chat_id in self.active_connections and user_id in self.active_connections[chat_id]:
            del self.active_connections[chat_id][user_id]
            if not self.active_connections[chat_id]:
                del self.active_connections[chat_id]

    async def broadcast(self, message: dict, chat_id: str, exclude_user_id: str = None):
        self.logger.info(self.active_connections)
        chat = ChatModel.model_validate(await chats_mongo_client.get_chat(chat_id))
        users = chat.participants
        is_op_in_chat = False
        if chat_id in self.active_connections:
            self.logger.info(chat_id)
            for user_id, connection in self.active_connections[chat_id].items():
                self.logger.info(f'user_id={user_id}, connection={connection}')
                if user_id in users and users[user_id] == 'operator':
                    is_op_in_chat = True
                if exclude_user_id and user_id != exclude_user_id:
                    message_string = json.dumps(message, default=str)
                    await connection.send_text(message_string)
        if not is_op_in_chat and message['type'] != 'system':
            await fb_client.send_push_notification(chat_id, message)