"""Contact endpoints"""
from fastapi import APIRouter, Depends, Query
from typing import List
from supabase import Client

from app.db.supabase_client import get_supabase
from app.schemas.contact import ContactCreate, ContactUpdate, ContactResponse
from app.schemas.auth import TokenData
from app.core.security import require_staff_or_owner
from app.services.base_service import BaseService

router = APIRouter()


@router.post("", response_model=ContactResponse)
async def create_contact(
    contact_data: ContactCreate,
    workspace_id: str = Query(...),
    current_user: TokenData = Depends(require_staff_or_owner),
    supabase: Client = Depends(get_supabase)
):
    """Create new contact (requires authentication)"""
    # Verify workspace_id matches user's workspace
    if workspace_id != current_user.workspace_id:
        from fastapi import HTTPException, status
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot create contacts for other workspaces"
        )
    
    service = BaseService(supabase, "contacts")
    contact = await service.create({
        **contact_data.model_dump(),
        "workspace_id": workspace_id
    })
    return ContactResponse(**contact)


@router.get("", response_model=List[ContactResponse])
async def get_contacts(
    current_user: TokenData = Depends(require_staff_or_owner),
    supabase: Client = Depends(get_supabase)
):
    """Get all contacts for workspace"""
    service = BaseService(supabase, "contacts")
    contacts = await service.get_all({"workspace_id": current_user.workspace_id})
    return [ContactResponse(**c) for c in contacts]


@router.get("/{contact_id}", response_model=ContactResponse)
async def get_contact(
    contact_id: str,
    current_user: TokenData = Depends(require_staff_or_owner),
    supabase: Client = Depends(get_supabase)
):
    """Get contact by ID"""
    service = BaseService(supabase, "contacts")
    contact = await service.get_by_id(contact_id)
    return ContactResponse(**contact)


@router.patch("/{contact_id}", response_model=ContactResponse)
async def update_contact(
    contact_id: str,
    contact_data: ContactUpdate,
    current_user: TokenData = Depends(require_staff_or_owner),
    supabase: Client = Depends(get_supabase)
):
    """Update contact"""
    service = BaseService(supabase, "contacts")
    contact = await service.update(contact_id, contact_data.model_dump(exclude_unset=True))
    return ContactResponse(**contact)
