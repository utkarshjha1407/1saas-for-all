"""Form endpoints"""
from fastapi import APIRouter, Depends, Query
from typing import List
from supabase import Client

from app.db.supabase_client import get_supabase
from app.schemas.form import (
    FormTemplateCreate,
    FormTemplateResponse,
    FormSubmissionCreate,
    FormSubmissionResponse,
)
from app.schemas.auth import TokenData
from app.core.security import get_current_user, require_owner
from app.services.base_service import BaseService

router = APIRouter()


@router.post("/templates", response_model=FormTemplateResponse)
async def create_form_template(
    form_data: FormTemplateCreate,
    current_user: TokenData = Depends(require_owner),
    supabase: Client = Depends(get_supabase)
):
    """Create form template"""
    service = BaseService(supabase, "form_templates")
    form = await service.create({
        **form_data.model_dump(),
        "workspace_id": current_user.workspace_id
    })
    return FormTemplateResponse(**form)


@router.get("/templates", response_model=List[FormTemplateResponse])
async def get_form_templates(
    current_user: TokenData = Depends(get_current_user),
    supabase: Client = Depends(get_supabase)
):
    """Get all form templates"""
    service = BaseService(supabase, "form_templates")
    forms = await service.get_all({"workspace_id": current_user.workspace_id})
    return [FormTemplateResponse(**f) for f in forms]


@router.post("/submissions", response_model=FormSubmissionResponse)
async def submit_form(
    submission_data: FormSubmissionCreate,
    supabase: Client = Depends(get_supabase)
):
    """Submit form (public endpoint)"""
    service = BaseService(supabase, "form_submissions")
    submission = await service.create({
        **submission_data.model_dump(),
        "status": "pending"
    })
    return FormSubmissionResponse(**submission)


@router.get("/submissions", response_model=List[FormSubmissionResponse])
async def get_form_submissions(
    status: str = Query(None),
    current_user: TokenData = Depends(get_current_user),
    supabase: Client = Depends(get_supabase)
):
    """Get form submissions"""
    service = BaseService(supabase, "form_submissions")
    
    filters = {"workspace_id": current_user.workspace_id}
    if status:
        filters["status"] = status
    
    submissions = await service.get_all(filters)
    return [FormSubmissionResponse(**s) for s in submissions]
