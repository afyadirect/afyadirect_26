# app/models/chat.py
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field
from enum import Enum

class MessageType(str, Enum):
    TEXT = "text"
    IMAGE = "image"
    FILE = "file"

class ChatMessage(BaseModel):
    id: str
    appointmentId: str
    senderId: str
    receiverId: str
    message: str
    attachmentUrl: Optional[str] = None
    type: MessageType = MessageType.TEXT
    isRead: bool = False
    sentAt: datetime = Field(default_factory=datetime.utcnow)
    deliveredAt: Optional[datetime] = None
    readAt: Optional[datetime] = None