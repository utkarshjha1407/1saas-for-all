"""Staff management service"""
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from supabase import Client
import structlog
import secrets
from app.core.security import hash_password

logger = structlog.get_logger()


class StaffService:
    """Service for managing staff invitations and permissions"""
    
    def __init__(self, supabase: Client):
        self.supabase = supabase
    
    async def invite_staff(self, workspace_id: str, email: str, invited_by: str, permissions: Dict[str, bool]) -> Dict[str, Any]:
        """Create staff invitation"""
        try:
            # Check if user already exists in workspace
            existing_user = (
                self.supabase.table("users")
                .select("*")
                .eq("email", email)
                .eq("workspace_id", workspace_id)
                .execute()
            )
            
            if existing_user.data:
                raise Exception("User already exists in this workspace")
            
            # Check for pending invitation
            existing_invitation = (
                self.supabase.table("staff_invitations")
                .select("*")
                .eq("email", email)
                .eq("workspace_id", workspace_id)
                .eq("status", "pending")
                .execute()
            )
            
            if existing_invitation.data:
                raise Exception("Pending invitation already exists for this email")
            
            # Generate invitation token
            token = secrets.token_urlsafe(32)
            
            # Create invitation
            invitation_data = {
                "workspace_id": workspace_id,
                "email": email,
                "invited_by": invited_by,
                "token": token,
                "permissions": permissions,
                "status": "pending",
                "expires_at": (datetime.now() + timedelta(days=7)).isoformat()
            }
            
            response = self.supabase.table("staff_invitations").insert(invitation_data).execute()
            
            if not response.data:
                raise Exception("Failed to create invitation")
            
            logger.info("staff_invitation_created", 
                       workspace_id=workspace_id,
                       email=email,
                       invitation_id=response.data[0]["id"])
            
            return response.data[0]
            
        except Exception as e:
            logger.error("invite_staff_failed", error=str(e))
            raise
    
    async def get_invitations(self, workspace_id: str, status: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get staff invitations for workspace"""
        try:
            query = self.supabase.table("staff_invitations").select("*").eq("workspace_id", workspace_id)
            
            if status:
                query = query.eq("status", status)
            
            response = query.order("created_at", desc=True).execute()
            return response.data or []
            
        except Exception as e:
            logger.error("get_invitations_failed", error=str(e))
            raise
    
    async def get_invitation_by_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Get invitation by token"""
        try:
            response = (
                self.supabase.table("staff_invitations")
                .select("*, workspaces(name)")
                .eq("token", token)
                .single()
                .execute()
            )
            
            return response.data
            
        except Exception as e:
            logger.error("get_invitation_by_token_failed", error=str(e))
            return None
    
    async def accept_invitation(self, token: str, full_name: str, password: str) -> Dict[str, Any]:
        """Accept staff invitation and create user"""
        try:
            # Get invitation
            invitation = await self.get_invitation_by_token(token)
            
            if not invitation:
                raise Exception("Invitation not found")
            
            if invitation["status"] != "pending":
                raise Exception("Invitation already used or expired")
            
            if datetime.fromisoformat(invitation["expires_at"]) < datetime.now():
                # Mark as expired
                self.supabase.table("staff_invitations").update({"status": "expired"}).eq("id", invitation["id"]).execute()
                raise Exception("Invitation has expired")
            
            # Create user
            user_data = {
                "email": invitation["email"],
                "password_hash": hash_password(password),
                "full_name": full_name,
                "role": "staff",
                "workspace_id": invitation["workspace_id"],
                "is_active": True
            }
            
            user_response = self.supabase.table("users").insert(user_data).execute()
            
            if not user_response.data:
                raise Exception("Failed to create user")
            
            user = user_response.data[0]
            
            # Create staff permissions
            permissions_data = {
                "user_id": user["id"],
                "workspace_id": invitation["workspace_id"],
                **invitation["permissions"]
            }
            
            self.supabase.table("staff_permissions").insert(permissions_data).execute()
            
            # Mark invitation as accepted
            self.supabase.table("staff_invitations").update({
                "status": "accepted",
                "accepted_at": datetime.now().isoformat()
            }).eq("id", invitation["id"]).execute()
            
            logger.info("staff_invitation_accepted",
                       invitation_id=invitation["id"],
                       user_id=user["id"])
            
            return user
            
        except Exception as e:
            logger.error("accept_invitation_failed", error=str(e))
            raise
    
    async def revoke_invitation(self, invitation_id: str) -> None:
        """Revoke pending invitation"""
        try:
            self.supabase.table("staff_invitations").update({
                "status": "expired"
            }).eq("id", invitation_id).execute()
            
            logger.info("invitation_revoked", invitation_id=invitation_id)
            
        except Exception as e:
            logger.error("revoke_invitation_failed", error=str(e))
            raise
    
    async def get_staff_members(self, workspace_id: str) -> List[Dict[str, Any]]:
        """Get all staff members for workspace"""
        try:
            # Get users
            users_response = (
                self.supabase.table("users")
                .select("*")
                .eq("workspace_id", workspace_id)
                .eq("role", "staff")
                .execute()
            )
            
            users = users_response.data or []
            
            # Get permissions for each user
            for user in users:
                permissions_response = (
                    self.supabase.table("staff_permissions")
                    .select("*")
                    .eq("user_id", user["id"])
                    .single()
                    .execute()
                )
                
                if permissions_response.data:
                    user["permissions"] = {
                        "can_access_inbox": permissions_response.data.get("can_access_inbox", True),
                        "can_manage_bookings": permissions_response.data.get("can_manage_bookings", True),
                        "can_view_forms": permissions_response.data.get("can_view_forms", True),
                        "can_view_inventory": permissions_response.data.get("can_view_inventory", True)
                    }
                else:
                    user["permissions"] = None
            
            return users
            
        except Exception as e:
            logger.error("get_staff_members_failed", error=str(e))
            raise
    
    async def update_staff_permissions(self, user_id: str, permissions: Dict[str, bool]) -> Dict[str, Any]:
        """Update staff member permissions"""
        try:
            response = (
                self.supabase.table("staff_permissions")
                .update(permissions)
                .eq("user_id", user_id)
                .execute()
            )
            
            if not response.data:
                raise Exception("Failed to update permissions")
            
            logger.info("staff_permissions_updated", user_id=user_id)
            
            return response.data[0]
            
        except Exception as e:
            logger.error("update_staff_permissions_failed", error=str(e))
            raise
    
    async def remove_staff_member(self, user_id: str) -> None:
        """Remove staff member (deactivate)"""
        try:
            self.supabase.table("users").update({
                "is_active": False
            }).eq("id", user_id).execute()
            
            logger.info("staff_member_removed", user_id=user_id)
            
        except Exception as e:
            logger.error("remove_staff_member_failed", error=str(e))
            raise
    
    async def check_activation_requirements(self, workspace_id: str) -> Dict[str, Any]:
        """Check if workspace meets activation requirements"""
        try:
            # Use database function
            response = self.supabase.rpc(
                "check_workspace_activation_requirements",
                {"p_workspace_id": workspace_id}
            ).execute()
            
            checklist = response.data
            
            # Get current activation status
            workspace_response = (
                self.supabase.table("workspaces")
                .select("is_activated, activated_at")
                .eq("id", workspace_id)
                .single()
                .execute()
            )
            
            workspace = workspace_response.data
            
            # Build missing requirements list
            missing = []
            if not checklist.get("communication_connected"):
                missing.append("Connect at least one communication channel (Email or SMS)")
            if not checklist.get("booking_type_exists"):
                missing.append("Create at least one booking type")
            if not checklist.get("availability_defined"):
                missing.append("Define availability schedule")
            
            return {
                "is_activated": workspace.get("is_activated", False),
                "activated_at": workspace.get("activated_at"),
                "checklist": checklist,
                "can_activate": checklist.get("all_requirements_met", False),
                "missing_requirements": missing
            }
            
        except Exception as e:
            logger.error("check_activation_requirements_failed", error=str(e))
            raise
    
    async def activate_workspace(self, workspace_id: str) -> Dict[str, Any]:
        """Activate workspace"""
        try:
            # Check requirements
            requirements = await self.check_activation_requirements(workspace_id)
            
            if not requirements["can_activate"]:
                raise Exception(f"Cannot activate: {', '.join(requirements['missing_requirements'])}")
            
            # Activate workspace
            response = (
                self.supabase.table("workspaces")
                .update({
                    "is_activated": True,
                    "activated_at": datetime.now().isoformat(),
                    "status": "active"
                })
                .eq("id", workspace_id)
                .execute()
            )
            
            if not response.data:
                raise Exception("Failed to activate workspace")
            
            logger.info("workspace_activated", workspace_id=workspace_id)
            
            return response.data[0]
            
        except Exception as e:
            logger.error("activate_workspace_failed", error=str(e))
            raise
