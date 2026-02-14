"""Form schemas"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from app.models.enums import FormStatus


class FormTemplateCreate(BaseModel):
    """Create form template schema"""
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    fields: List[Dict[str, Any]]  # JSON schema for form fields
    booking_type_ids: List[str] = []


class FormTemplateResponse(BaseModel):
    """Form template response schema"""
    id: str
    workspace_id: str
    name: str
    description: Optional[str]
    fields: List[Dict[str, Any]]
    booking_type_ids: List[str]
    created_at: datetime
    
    class Config:
        from_attributes = True


class FormSubmissionCreate(BaseModel):
    """Create form submission schema"""
    form_template_id: str
    booking_id: str
    data: Dict[str, Any]


class FormSubmissionPublicCreate(BaseModel):
    """Public form submission (from customer)"""
    data: Dict[str, Any]


class FormSubmissionResponse(BaseModel):
    """Form submission response schema"""
    id: str
    form_template_id: str
    booking_id: str
    contact_id: str
    status: FormStatus
    data: Dict[str, Any]
    submitted_at: Optional[datetime]
    created_at: datetime
    access_token: Optional[str] = None
    public_url: Optional[str] = None
    
    class Config:
        from_attributes = True
