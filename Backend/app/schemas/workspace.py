"""Workspace schemas"""
from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime
from app.models.enums import WorkspaceStatus, OnboardingStep


class WorkspaceCreate(BaseModel):
    """Create workspace schema"""
    name: str = Field(..., min_length=1, max_length=255)
    address: str = Field(..., min_length=1)
    timezone: str = Field(default="UTC")
    contact_email: EmailStr
    slug: Optional[str] = None


class WorkspaceUpdate(BaseModel):
    """Update workspace schema"""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    address: Optional[str] = None
    timezone: Optional[str] = None
    contact_email: Optional[EmailStr] = None
    slug: Optional[str] = None
    logo_url: Optional[str] = None
    primary_color: Optional[str] = None
    secondary_color: Optional[str] = None


class WorkspaceResponse(BaseModel):
    """Workspace response schema"""
    id: str
    name: str
    address: str
    timezone: str
    contact_email: str
    status: WorkspaceStatus
    onboarding_step: OnboardingStep
    owner_id: str
    slug: Optional[str] = None
    logo_url: Optional[str] = None
    primary_color: Optional[str] = "#3b82f6"
    secondary_color: Optional[str] = "#8b5cf6"
    is_onboarding_complete: bool = False
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class WorkspacePublicResponse(BaseModel):
    """Public workspace information (no sensitive data)"""
    id: str
    name: str
    slug: str
    logo_url: Optional[str] = None
    primary_color: str = "#3b82f6"
    secondary_color: str = "#8b5cf6"


class OnboardingStatus(BaseModel):
    """Onboarding status response"""
    current_step: OnboardingStep
    completed_steps: List[OnboardingStep]
    is_complete: bool
    next_step: Optional[OnboardingStep]
    missing_requirements: List[str]


class PublicURLsResponse(BaseModel):
    """Public URLs for workspace"""
    contact_form: str
    booking_page: str
    workspace_slug: str


class SlugCheckResponse(BaseModel):
    """Slug availability check response"""
    available: bool
    suggested_slug: Optional[str] = None
