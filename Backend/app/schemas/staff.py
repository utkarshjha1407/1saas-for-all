"""Staff management schemas"""
from pydantic import BaseModel, Field, EmailStr
from typing import Optional
from datetime import datetime


class StaffPermissions(BaseModel):
    """Staff permissions schema"""
    can_access_inbox: bool = True
    can_manage_bookings: bool = True
    can_view_forms: bool = True
    can_view_inventory: bool = True


class StaffInvitationCreate(BaseModel):
    """Create staff invitation schema"""
    email: EmailStr = Field(..., description="Email address to invite")
    permissions: StaffPermissions = Field(default_factory=StaffPermissions)


class StaffInvitationResponse(BaseModel):
    """Staff invitation response schema"""
    id: str
    workspace_id: str
    email: str
    invited_by: str
    token: str
    permissions: dict
    status: str
    expires_at: datetime
    accepted_at: Optional[datetime]
    created_at: datetime
    
    class Config:
        from_attributes = True


class StaffInvitationAccept(BaseModel):
    """Accept staff invitation schema"""
    token: str
    full_name: str
    password: str = Field(..., min_length=8)


class StaffPermissionsUpdate(BaseModel):
    """Update staff permissions schema"""
    can_access_inbox: Optional[bool] = None
    can_manage_bookings: Optional[bool] = None
    can_view_forms: Optional[bool] = None
    can_view_inventory: Optional[bool] = None


class StaffMemberResponse(BaseModel):
    """Staff member response schema"""
    id: str
    email: str
    full_name: str
    role: str
    is_active: bool
    permissions: Optional[StaffPermissions]
    created_at: datetime
    
    class Config:
        from_attributes = True


class WorkspaceActivationChecklist(BaseModel):
    """Workspace activation checklist"""
    communication_connected: bool
    booking_type_exists: bool
    availability_defined: bool
    all_requirements_met: bool


class WorkspaceActivationResponse(BaseModel):
    """Workspace activation response"""
    is_activated: bool
    activated_at: Optional[datetime]
    checklist: WorkspaceActivationChecklist
    can_activate: bool
    missing_requirements: list[str]
