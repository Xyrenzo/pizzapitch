from pydantic import BaseModel
from typing import Optional, Dict, Any

class UserSession(BaseModel):
    user_id: int
    ip_address: str

class QuizResults(BaseModel):
    A: int
    B: int
    C: int
    D: int

class ChatMessage(BaseModel):
    message: str

class CreateChatRequest(BaseModel):
    title: str = "Новый чат"