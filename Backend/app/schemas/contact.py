"""Contact schemas"""
from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime


class ContactCreate(BaseModel):
    """Create contact schema"""
    name: str
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    message: Optional[str] = None


class ContactUpdate(BaseModel):
    """Update contact schema"""
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None


class ContactResponse(BaseModel):
    """Contact response schema"""
    id: str
    workspace_id: str
    name: str
    email: Optional[str]
    phone: Optional[str]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True
