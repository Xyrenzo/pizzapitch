from fastapi import APIRouter, Request, Depends, Query
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from chat.bot import CareerGuideBot
from chat.models import ChatMessage, CreateChatRequest
from config import TEMPLATES_DIR, STATIC_DIR
from fastapi.staticfiles import StaticFiles

router = APIRouter(prefix="/chat", tags=["chat"])
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))
router.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
chat_bot = CareerGuideBot()


async def get_user_id(user_id: int = Query(...)):
    return user_id

@router.get('', response_class=HTMLResponse)
def chat_bot_page(request: Request, user_id: int = Depends(get_user_id)):
    return templates.TemplateResponse("chat_bot.html", {
        "request": request,
        "user_id": user_id
    })

@router.get('/chats')
async def get_user_chats(user_id: int = Depends(get_user_id)):
    try:
        chats = chat_bot.get_chats(user_id)
        active_chat = chat_bot.get_active_chat(user_id)
        return {
            "status": "success",
            "chats": chats,
            "active_chat": active_chat
        }
    except Exception as e:
        return {"status": "error", "error": str(e)}

@router.post('/create')
async def create_chat(
    create_request: CreateChatRequest,
    user_id: int = Depends(get_user_id)
):
    try:
        chat_id = chat_bot.create_chat(user_id, create_request.title)
        return {
            "status": "success",
            "chat_id": chat_id
        }
    except Exception as e:
        return {"status": "error", "error": str(e)}

@router.post('/{chat_id}/set_active')
async def set_active_chat(
    chat_id: int,
    user_id: int = Depends(get_user_id)
):
    try:
        print(f"Setting active chat {chat_id} for user {user_id}")
        success = chat_bot.set_active_chat(user_id, chat_id)
        if success:
            return {"status": "success"}
        else:
            return {"status": "error", "error": "Chat not found"}
    except Exception as e:
        return {"status": "error", "error": str(e)}

@router.delete('/{chat_id}')
async def delete_chat(
    chat_id: int,
    user_id: int = Depends(get_user_id)
):
    try:
        print(f"Deleting chat {chat_id} for user {user_id}")
        success = chat_bot.delete_chat(user_id, chat_id)
        if success:
            return {"status": "success"}
        else:
            return {"status": "error", "error": "Chat not found"}
    except Exception as e:
        return {"status": "error", "error": str(e)}

@router.get('/messages')
async def get_chat_messages(user_id: int = Depends(get_user_id)):
    try:
        active_chat = chat_bot.get_active_chat(user_id)
        if not active_chat:
            return {"status": "success", "messages": []}

        messages = chat_bot.get_messages(active_chat["id"])
        return {
            "status": "success",
            "messages": messages,
            "active_chat": active_chat
        }
    except Exception as e:
        return {"status": "error", "error": str(e)}

@router.post('/send')
async def send_message(
    chat_message: ChatMessage,
    user_id: int = Depends(get_user_id)
):
    try:
        response = chat_bot.get_response(user_id, chat_message.message)
        return {
            "status": "success",
            "response": response
        }
    except Exception as e:
        return {"status": "error", "error": str(e)}
