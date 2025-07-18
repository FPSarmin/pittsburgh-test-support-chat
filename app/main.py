from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request
from fastapi.templating import Jinja2Templates
from starlette.responses import HTMLResponse

from app.api.chat_ws import chat_ws_router
from app.api.chats import chat_router
from app.models.chat_mongo_client import ChatsMongoClient

app = FastAPI()
templates = Jinja2Templates(directory="templates")
app.include_router(chat_router)
app.include_router(chat_ws_router)
# Show test page with common chat
@app.get("/", response_class=HTMLResponse)
def read_index(request: Request):
    return templates.TemplateResponse("user.html", {"request" : request})
