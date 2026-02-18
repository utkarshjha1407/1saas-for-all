"""Form schemas"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from app.models.enums import FormStatus


class FormTemplateCreate(BaseModel):
    """Create form template schema (file upload)"""
    name: str = Field(..., min_length=1, max_length=255, description="Form name")
    description: Optional[str] = Field(None, description="Form description")
    file_url: str = Field(..., description="URL to uploaded file (PDF, DOCX, etc.)")
    file_type: Optional[str] = Field(None, description="File type (pdf, docx, doc)")
    file_size: Optional[int] = Field(None, description="File size in bytes")
    booking_type_ids: List[str] = Field(default_factory=list, description="Booking types that require this form")


class FormTemplateUpdate(BaseModel):
    """Update form template schema"""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    file_url: Optional[str] = None
    file_type: Optional[str] = None
    file_size: Optional[int] = None
    booking_type_ids: Optional[List[str]] = None


class FormTemplateResponse(BaseModel):
    """Form template response schema"""
    id: str
    workspace_id: str
    name: str
    description: Optional[str]
    file_url: str
    file_type: Optional[str]
    file_size: Optional[int]
    booking_type_ids: List[str]
    created_at: datetime
    
    class Config:
        from_attributes = True


class FormSubmissionCreate(BaseModel):
    """Create form submission schema"""
    form_template_id: str
    booking_id: str
    contact_id: str
    status: str = "pending"
    data: Dict[str, Any] = Field(default_factory=dict)


class FormSubmissionUpdate(BaseModel):
    """Update form submission schema"""
    status: Optional[str] = None
    data: Optional[Dict[str, Any]] = None
    viewed_at: Optional[datetime] = None
    downloaded_at: Optional[datetime] = None
    submitted_at: Optional[datetime] = None


class FormSubmissionPublicCreate(BaseModel):
    """Public form submission (from customer)"""
    data: Dict[str, Any]


class FormSubmissionResponse(BaseModel):
    """Form submission response schema"""
    id: str
    form_template_id: str
    booking_id: str
    contact_id: str
    workspace_id: str
    status: str
    data: Dict[str, Any]
    submitted_at: Optional[datetime]
    viewed_at: Optional[datetime]
    downloaded_at: Optional[datetime]
    created_at: datetime
    access_token: Optional[str] = None
    public_url: Optional[str] = None
    
    class Config:
        from_attributes = True
