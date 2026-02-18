"""Contact form management endpoints"""
from fastapi import APIRouter, Depends, HTTPException, status
from supabase import Client
from pydantic import BaseModel
from typing import Dict, Any, Optional

from app.db.supabase_client import get_supabase
from app.schemas.auth import TokenData
from app.core.security import require_owner
from app.services.contact_form_service import ContactFormService
from app.core.exceptions import ValidationException

router = APIRouter()


class ContactFormConfig(BaseModel):
    """Contact form configuration"""
    name: str
    description: str
    fields: list
    submit_button_text: str
    success_message: str
    welcome_message: str


class ContactFormResponse(BaseModel):
    """Contact form response"""
    id: str
    workspace_id: str
    name: str
    description: str
    fields: list
    submit_button_text: str
    success_message: str
    welcome_message: str
    is_active: bool
    public_url: Optional[str] = None


@router.get("", response_model=Optional[ContactFormResponse])
async def get_contact_form(
    current_user: TokenData = Depends(require_owner),
    supabase: Client = Depends(get_supabase)
):
    """Get workspace contact form configuration"""
    service = ContactFormService(supabase)
    form = await service.get_workspace_form(current_user.workspace_id)
    
    if form:
        # Get workspace slug for public URL
        workspace = await supabase.table("workspaces").select("slug").eq("id", current_user.workspace_id).single().execute()
        slug = workspace.data.get("slug") if workspace.data else None
        
        return ContactFormResponse(
            **form,
            public_url=f"/public/{slug}/contact" if slug else None
        )
    
    return None


@router.post("", response_model=ContactFormResponse, status_code=status.HTTP_201_CREATED)
async def create_or_update_contact_form(
    form_config: ContactFormConfig,
    current_user: TokenData = Depends(require_owner),
    supabase: Client = Depends(get_supabase)
):
    """Create or update contact form"""
    try:
        service = ContactFormService(supabase)
        
        # Validate form configuration
        await service.validate_form_config(form_config.model_dump())
        
        # Create or update form
        form = await service.create_or_update_form(
            current_user.workspace_id,
            form_config.model_dump()
        )
        
        # Get workspace slug for public URL
        workspace = await supabase.table("workspaces").select("slug").eq("id", current_user.workspace_id).single().execute()
        slug = workspace.data.get("slug") if workspace.data else None
        
        return ContactFormResponse(
            **form,
            public_url=f"/public/{slug}/contact" if slug else None
        )
    except ValidationException as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/stats")
async def get_form_stats(
    current_user: TokenData = Depends(require_owner),
    supabase: Client = Depends(get_supabase)
):
    """Get contact form statistics"""
    service = ContactFormService(supabase)
    
    submissions_count = await service.get_form_submissions_count(current_user.workspace_id)
    
    # Get recent submissions
    recent = (
        supabase.table("contacts")
        .select("*")
        .eq("workspace_id", current_user.workspace_id)
        .eq("source", "contact_form")
        .order("created_at", desc=True)
        .limit(5)
        .execute()
    )
    
    return {
        "total_submissions": submissions_count,
        "recent_submissions": recent.data
    }
