"""Message and conversation schemas"""
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from app.models.enums import CommunicationChannel, MessageType


class MessageCreate(BaseModel):
    """Create message schema"""
    conversation_id: str
    content: str
    channel: CommunicationChannel
    is_automated: bool = False


class MessageResponse(BaseModel):
    """Message response schema"""
    id: str
    conversation_id: str
    sender_id: Optional[str]  # None for automated messages
    content: str
    channel: CommunicationChannel
    message_type: MessageType
    is_read: bool
    sent_at: datetime
    
    class Config:
        from_attributes = True


class ConversationResponse(BaseModel):
    """Conversation response schema"""
    id: str
    workspace_id: str
    contact_id: str
    last_message_at: datetime
    unread_count: int
    is_automated_paused: bool
    created_at: datetime
    
    class Config:
        from_attributes = True
