"""Message and conversation endpoints"""
from fastapi import APIRouter, Depends
from typing import List
from supabase import Client

from app.db.supabase_client import get_supabase
from app.schemas.message import MessageCreate, MessageResponse, ConversationResponse
from app.schemas.auth import TokenData
from app.core.security import require_staff_or_owner
from app.services.base_service import BaseService

router = APIRouter()


@router.get("/conversations", response_model=List[ConversationResponse])
async def get_conversations(
    current_user: TokenData = Depends(require_staff_or_owner),
    supabase: Client = Depends(get_supabase)
):
    """Get all conversations for workspace"""
    service = BaseService(supabase, "conversations")
    conversations = await service.get_all({"workspace_id": current_user.workspace_id})
    return [ConversationResponse(**c) for c in conversations]


@router.get("/conversations/{conversation_id}/messages", response_model=List[MessageResponse])
async def get_conversation_messages(
    conversation_id: str,
    current_user: TokenData = Depends(require_staff_or_owner),
    supabase: Client = Depends(get_supabase)
):
    """Get messages for a conversation"""
    service = BaseService(supabase, "messages")
    messages = await service.get_all({"conversation_id": conversation_id})
    return [MessageResponse(**m) for m in messages]


@router.post("/conversations/{conversation_id}/messages", response_model=MessageResponse)
async def send_message(
    conversation_id: str,
    message_data: MessageCreate,
    current_user: TokenData = Depends(require_staff_or_owner),
    supabase: Client = Depends(get_supabase)
):
    """Send message in conversation"""
    service = BaseService(supabase, "messages")
    message = await service.create({
        **message_data.model_dump(),
        "sender_id": current_user.user_id,
        "message_type": "manual"
    })
    
    # Pause automation when staff replies
    conv_service = BaseService(supabase, "conversations")
    await conv_service.update(conversation_id, {"is_automated_paused": True})
    
    return MessageResponse(**message)


@router.post("/conversations/{conversation_id}/mark-read")
async def mark_conversation_read(
    conversation_id: str,
    current_user: TokenData = Depends(require_staff_or_owner),
    supabase: Client = Depends(get_supabase)
):
    """Mark all messages in conversation as read"""
    supabase.table("messages").update({"is_read": True}).eq("conversation_id", conversation_id).execute()
    return {"success": True}
