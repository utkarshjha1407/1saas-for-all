"""Staff management endpoints"""
from fastapi import APIRouter, Depends, Query, HTTPException, status
from typing import List
from supabase import Client
import structlog

from app.db.supabase_client import get_supabase
from app.schemas.staff import (
    StaffInvitationCreate,
    StaffInvitationResponse,
    StaffInvitationAccept,
    StaffPermissionsUpdate,
    StaffMemberResponse,
    WorkspaceActivationResponse,
)
from app.schemas.auth import TokenData
from app.core.security import require_owner, require_staff_or_owner
from app.services.staff_service import StaffService

router = APIRouter()
logger = structlog.get_logger()


@router.post("/invitations", response_model=StaffInvitationResponse, status_code=status.HTTP_201_CREATED)
async def invite_staff_member(
    invitation_data: StaffInvitationCreate,
    current_user: TokenData = Depends(require_owner),
    supabase: Client = Depends(get_supabase)
):
    """Invite staff member (Owner only)"""
    try:
        service = StaffService(supabase)
        invitation = await service.invite_staff(
            workspace_id=current_user.workspace_id,
            email=invitation_data.email,
            invited_by=current_user.user_id,
            permissions=invitation_data.permissions.model_dump()
        )
        
        # TODO: Send invitation email
        
        return StaffInvitationResponse(**invitation)
        
    except Exception as e:
        logger.error("invite_staff_failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/invitations", response_model=List[StaffInvitationResponse])
async def get_staff_invitations(
    status_filter: str = Query(None, alias="status"),
    current_user: TokenData = Depends(require_owner),
    supabase: Client = Depends(get_supabase)
):
    """Get staff invitations (Owner only)"""
    try:
        service = StaffService(supabase)
        invitations = await service.get_invitations(current_user.workspace_id, status_filter)
        return [StaffInvitationResponse(**inv) for inv in invitations]
        
    except Exception as e:
        logger.error("get_invitations_failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get invitations"
        )


@router.post("/invitations/{invitation_id}/revoke", status_code=status.HTTP_204_NO_CONTENT)
async def revoke_staff_invitation(
    invitation_id: str,
    current_user: TokenData = Depends(require_owner),
    supabase: Client = Depends(get_supabase)
):
    """Revoke staff invitation (Owner only)"""
    try:
        service = StaffService(supabase)
        await service.revoke_invitation(invitation_id)
        return None
        
    except Exception as e:
        logger.error("revoke_invitation_failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to revoke invitation"
        )


@router.post("/invitations/accept", status_code=status.HTTP_201_CREATED)
async def accept_staff_invitation(
    accept_data: StaffInvitationAccept,
    supabase: Client = Depends(get_supabase)
):
    """Accept staff invitation (Public endpoint)"""
    try:
        service = StaffService(supabase)
        user = await service.accept_invitation(
            token=accept_data.token,
            full_name=accept_data.full_name,
            password=accept_data.password
        )
        
        return {
            "message": "Invitation accepted successfully",
            "user_id": user["id"],
            "email": user["email"]
        }
        
    except Exception as e:
        logger.error("accept_invitation_failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/invitations/verify/{token}")
async def verify_invitation_token(
    token: str,
    supabase: Client = Depends(get_supabase)
):
    """Verify invitation token (Public endpoint)"""
    try:
        service = StaffService(supabase)
        invitation = await service.get_invitation_by_token(token)
        
        if not invitation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Invitation not found"
            )
        
        if invitation["status"] != "pending":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invitation already used or expired"
            )
        
        from datetime import datetime
        if datetime.fromisoformat(invitation["expires_at"]) < datetime.now():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invitation has expired"
            )
        
        return {
            "valid": True,
            "email": invitation["email"],
            "workspace_name": invitation["workspaces"]["name"],
            "permissions": invitation["permissions"]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("verify_invitation_failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to verify invitation"
        )


@router.get("/members", response_model=List[StaffMemberResponse])
async def get_staff_members(
    current_user: TokenData = Depends(require_owner),
    supabase: Client = Depends(get_supabase)
):
    """Get staff members (Owner only)"""
    try:
        service = StaffService(supabase)
        members = await service.get_staff_members(current_user.workspace_id)
        return [StaffMemberResponse(**member) for member in members]
        
    except Exception as e:
        logger.error("get_staff_members_failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get staff members"
        )


@router.put("/members/{user_id}/permissions")
async def update_staff_permissions(
    user_id: str,
    permissions_data: StaffPermissionsUpdate,
    current_user: TokenData = Depends(require_owner),
    supabase: Client = Depends(get_supabase)
):
    """Update staff permissions (Owner only)"""
    try:
        service = StaffService(supabase)
        permissions = await service.update_staff_permissions(
            user_id,
            permissions_data.model_dump(exclude_unset=True)
        )
        return permissions
        
    except Exception as e:
        logger.error("update_permissions_failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update permissions"
        )


@router.delete("/members/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_staff_member(
    user_id: str,
    current_user: TokenData = Depends(require_owner),
    supabase: Client = Depends(get_supabase)
):
    """Remove staff member (Owner only)"""
    try:
        service = StaffService(supabase)
        await service.remove_staff_member(user_id)
        return None
        
    except Exception as e:
        logger.error("remove_staff_failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to remove staff member"
        )


@router.get("/activation", response_model=WorkspaceActivationResponse)
async def check_workspace_activation(
    current_user: TokenData = Depends(require_owner),
    supabase: Client = Depends(get_supabase)
):
    """Check workspace activation status (Owner only)"""
    try:
        service = StaffService(supabase)
        activation_status = await service.check_activation_requirements(current_user.workspace_id)
        return WorkspaceActivationResponse(**activation_status)
        
    except Exception as e:
        logger.error("check_activation_failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to check activation status"
        )


@router.post("/activation/activate")
async def activate_workspace(
    current_user: TokenData = Depends(require_owner),
    supabase: Client = Depends(get_supabase)
):
    """Activate workspace (Owner only)"""
    try:
        service = StaffService(supabase)
        workspace = await service.activate_workspace(current_user.workspace_id)
        
        return {
            "message": "Workspace activated successfully",
            "workspace_id": workspace["id"],
            "activated_at": workspace["activated_at"]
        }
        
    except Exception as e:
        logger.error("activate_workspace_failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
