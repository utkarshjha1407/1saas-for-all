"""Form endpoints"""
from fastapi import APIRouter, Depends, Query, HTTPException
from typing import List
from supabase import Client
import logging

from app.db.supabase_client import get_supabase
from app.schemas.form import (
    FormTemplateCreate,
    FormTemplateUpdate,
    FormTemplateResponse,
    FormSubmissionCreate,
    FormSubmissionUpdate,
    FormSubmissionResponse,
)
from app.schemas.auth import TokenData
from app.core.security import require_owner, require_staff_or_owner
from app.services.base_service import BaseService

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/templates", response_model=FormTemplateResponse, status_code=201)
async def create_form_template(
    form_data: FormTemplateCreate,
    current_user: TokenData = Depends(require_owner),
    supabase: Client = Depends(get_supabase)
):
    """Create form template (Owner only)"""
    try:
        service = BaseService(supabase, "form_templates")
        form = await service.create({
            **form_data.model_dump(),
            "workspace_id": current_user.workspace_id
        })
        return FormTemplateResponse(**form)
    except Exception as e:
        logger.error(f"Error creating form template: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to create form template")


@router.get("/templates", response_model=List[FormTemplateResponse])
async def get_form_templates(
    current_user: TokenData = Depends(require_staff_or_owner),
    supabase: Client = Depends(get_supabase)
):
    """Get all form templates (Staff or Owner)"""
    try:
        service = BaseService(supabase, "form_templates")
        forms = await service.get_all({"workspace_id": current_user.workspace_id})
        return [FormTemplateResponse(**f) for f in forms]
    except Exception as e:
        logger.error(f"Error getting form templates: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get form templates")


@router.get("/templates/{template_id}", response_model=FormTemplateResponse)
async def get_form_template(
    template_id: str,
    current_user: TokenData = Depends(require_staff_or_owner),
    supabase: Client = Depends(get_supabase)
):
    """Get single form template (Staff or Owner)"""
    try:
        service = BaseService(supabase, "form_templates")
        form = await service.get_by_id(template_id)
        
        if not form:
            raise HTTPException(status_code=404, detail="Form template not found")
        
        if form["workspace_id"] != current_user.workspace_id:
            raise HTTPException(status_code=403, detail="Access denied")
        
        return FormTemplateResponse(**form)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting form template: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get form template")


@router.put("/templates/{template_id}", response_model=FormTemplateResponse)
async def update_form_template(
    template_id: str,
    form_data: FormTemplateUpdate,
    current_user: TokenData = Depends(require_owner),
    supabase: Client = Depends(get_supabase)
):
    """Update form template (Owner only)"""
    try:
        service = BaseService(supabase, "form_templates")
        
        # Verify exists and belongs to workspace
        existing = await service.get_by_id(template_id)
        if not existing:
            raise HTTPException(status_code=404, detail="Form template not found")
        
        if existing["workspace_id"] != current_user.workspace_id:
            raise HTTPException(status_code=403, detail="Access denied")
        
        form = await service.update(template_id, form_data.model_dump(exclude_unset=True))
        return FormTemplateResponse(**form)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating form template: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to update form template")


@router.delete("/templates/{template_id}", status_code=204)
async def delete_form_template(
    template_id: str,
    current_user: TokenData = Depends(require_owner),
    supabase: Client = Depends(get_supabase)
):
    """Delete form template (Owner only)"""
    try:
        service = BaseService(supabase, "form_templates")
        
        # Verify exists and belongs to workspace
        existing = await service.get_by_id(template_id)
        if not existing:
            raise HTTPException(status_code=404, detail="Form template not found")
        
        if existing["workspace_id"] != current_user.workspace_id:
            raise HTTPException(status_code=403, detail="Access denied")
        
        await service.delete(template_id)
        return None
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting form template: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to delete form template")


@router.get("/submissions", response_model=List[FormSubmissionResponse])
async def get_form_submissions(
    status: str = Query(None),
    current_user: TokenData = Depends(require_staff_or_owner),
    supabase: Client = Depends(get_supabase)
):
    """Get form submissions (Staff or Owner)"""
    try:
        service = BaseService(supabase, "form_submissions")
        
        filters = {"workspace_id": current_user.workspace_id}
        if status:
            filters["status"] = status
        
        submissions = await service.get_all(filters)
        return [FormSubmissionResponse(**s) for s in submissions]
    except Exception as e:
        logger.error(f"Error getting form submissions: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get form submissions")


@router.put("/submissions/{submission_id}", response_model=FormSubmissionResponse)
async def update_form_submission(
    submission_id: str,
    submission_data: FormSubmissionUpdate,
    current_user: TokenData = Depends(require_staff_or_owner),
    supabase: Client = Depends(get_supabase)
):
    """Update form submission status (Staff or Owner)"""
    try:
        service = BaseService(supabase, "form_submissions")
        
        # Verify exists and belongs to workspace
        existing = await service.get_by_id(submission_id)
        if not existing:
            raise HTTPException(status_code=404, detail="Form submission not found")
        
        if existing["workspace_id"] != current_user.workspace_id:
            raise HTTPException(status_code=403, detail="Access denied")
        
        submission = await service.update(submission_id, submission_data.model_dump(exclude_unset=True))
        return FormSubmissionResponse(**submission)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating form submission: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to update form submission")
