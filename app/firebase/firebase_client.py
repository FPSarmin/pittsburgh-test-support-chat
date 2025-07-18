import logging

import firebase_admin
from firebase_admin import credentials, messaging
from firebase_admin.exceptions import FirebaseError

class FireBaseClient:
    def __init__(self):
        cred = credentials.Certificate("/app/google-services.json")
        self.firebase_app = firebase_admin.initialize_app(cred)
        self.logger = logging.getLogger('uvicorn.error')

    async def get_not_real_token(self, chat_id: str):
        return "some_token"

    async def get_any_not_real_token(self, chat_id: str):
        return "any_token"

    async def send_push_notification(self, chat_id: str, message: str):
        try:
            operator_fcm_token = await self.get_not_real_token(chat_id)
            if not operator_fcm_token:
                self.logger.warning(f"No FCM token found for operator in chat {chat_id}, preparing to choose someone")
                operator_fcm_token = await self.get_any_not_real_token(chat_id)

            notification = messaging.Notification(
                title="Новое сообщение в чате",
                body=f"Чат {chat_id}: {message[:50]}..."
            )

            message = messaging.Message(
                notification=notification,
                token=operator_fcm_token,
                data={
                    "chat_id": chat_id,
                    "type": "new_message"
                }
            )

            response = messaging.send(message)
            self.logger.info(f"Push notification sent: {response}")
        except FirebaseError as e:
            self.logger.error(f"Firebase error: {e}")
        except Exception as e:
            self.logger.error(f"Error sending push: {e}")


fb_client = FireBaseClient()