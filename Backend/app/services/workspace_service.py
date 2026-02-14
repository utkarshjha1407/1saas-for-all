"""Workspace service"""
from typing import Dict, Any, List, Optional
import re
import secrets
from supabase import Client

from app.services.base_service import BaseService
from app.models.enums import WorkspaceStatus, OnboardingStep
from app.core.exceptions import ValidationException


class WorkspaceService(BaseService):
    """Workspace management service"""
    
    def __init__(self, supabase: Client):
        super().__init__(supabase, "workspaces")
    
    async def create_workspace(self, data: Dict[str, Any], owner_id: str) -> Dict[str, Any]:
        """Create new workspace"""
        # Generate unique slug if not provided
        if "slug" not in data or not data["slug"]:
            data["slug"] = await self._generate_unique_slug(data["name"])
        
        workspace_data = {
            **data,
            "owner_id": owner_id,
            "status": WorkspaceStatus.SETUP.value,
            "onboarding_step": OnboardingStep.WORKSPACE_CREATED.value,
            "is_onboarding_complete": False,
        }
        
        return await self.create(workspace_data)
    
    async def get_onboarding_status(self, workspace_id: str) -> Dict[str, Any]:
        """Get workspace onboarding status"""
        workspace = await self.get_by_id(workspace_id)
        
        current_step = OnboardingStep(workspace["onboarding_step"])
        completed_steps = self._get_completed_steps(current_step)
        
        # Check requirements for activation
        missing_requirements = await self._check_activation_requirements(workspace_id)
        
        return {
            "current_step": current_step,
            "completed_steps": completed_steps,
            "is_complete": current_step == OnboardingStep.ACTIVATED,
            "next_step": self._get_next_step(current_step),
            "missing_requirements": missing_requirements,
        }
    
    async def update_onboarding_step(
        self, workspace_id: str, step: OnboardingStep
    ) -> Dict[str, Any]:
        """Update workspace onboarding step"""
        return await self.update(workspace_id, {"onboarding_step": step.value})
    
    async def activate_workspace(self, workspace_id: str) -> Dict[str, Any]:
        """Activate workspace after validation"""
        # Use database function to check requirements
        result = self.supabase.rpc(
            'check_workspace_activation_ready',
            {'p_workspace_id': workspace_id}
        ).execute()
        
        if result.data and not result.data.get('is_ready', False):
            missing = result.data.get('missing_items', [])
            raise ValidationException(
                f"Cannot activate workspace. Missing: {', '.join(missing)}"
            )
        
        return await self.update(
            workspace_id,
            {
                "status": WorkspaceStatus.ACTIVE.value,
                "onboarding_step": OnboardingStep.ACTIVATED.value,
                "is_onboarding_complete": True,
            }
        )
    
    async def get_by_slug(self, slug: str) -> Dict[str, Any]:
        """Get workspace by slug"""
        response = (
            self.supabase.table(self.table_name)
            .select("*")
            .eq("slug", slug)
            .eq("status", WorkspaceStatus.ACTIVE.value)
            .single()
            .execute()
        )
        
        if not response.data:
            raise ValidationException("Workspace not found or not active")
        
        return response.data
    
    async def check_slug_available(self, slug: str, exclude_workspace_id: Optional[str] = None) -> bool:
        """Check if slug is available"""
        query = self.supabase.table(self.table_name).select("id").eq("slug", slug)
        
        if exclude_workspace_id:
            query = query.neq("id", exclude_workspace_id)
        
        response = query.execute()
        return len(response.data) == 0
    
    async def get_public_urls(self, workspace_id: str) -> Dict[str, str]:
        """Get public URLs for workspace"""
        workspace = await self.get_by_id(workspace_id)
        slug = workspace.get("slug")
        
        if not slug:
            raise ValidationException("Workspace does not have a slug")
        
        base_url = "http://localhost:8080"  # TODO: Get from config
        
        return {
            "contact_form": f"{base_url}/public/{slug}/contact",
            "booking_page": f"{base_url}/public/{slug}/book",
            "workspace_slug": slug,
        }
    
    async def _generate_unique_slug(self, name: str) -> str:
        """Generate unique slug from workspace name"""
        # Convert to lowercase and replace spaces/special chars with hyphens
        slug = re.sub(r'[^a-z0-9]+', '-', name.lower()).strip('-')
        
        # Check if slug is available
        if await self.check_slug_available(slug):
            return slug
        
        # If not available, append random suffix
        for _ in range(10):
            suffix = secrets.token_hex(3)
            candidate = f"{slug}-{suffix}"
            if await self.check_slug_available(candidate):
                return candidate
        
        # Fallback to completely random slug
        return f"workspace-{secrets.token_hex(6)}"
    
    def _get_completed_steps(self, current_step: OnboardingStep) -> List[OnboardingStep]:
        """Get list of completed onboarding steps"""
        all_steps = list(OnboardingStep)
        current_index = all_steps.index(current_step)
        return all_steps[:current_index + 1]
    
    def _get_next_step(self, current_step: OnboardingStep) -> OnboardingStep:
        """Get next onboarding step"""
        all_steps = list(OnboardingStep)
        current_index = all_steps.index(current_step)
        
        if current_index < len(all_steps) - 1:
            return all_steps[current_index + 1]
        return None
    
    async def _check_activation_requirements(self, workspace_id: str) -> List[str]:
        """Check if workspace meets activation requirements"""
        missing = []
        
        # Check communication setup
        integrations = await self._get_workspace_integrations(workspace_id)
        if not integrations:
            missing.append("At least one communication channel")
        
        # Check booking types
        booking_types = await self._get_booking_types(workspace_id)
        if not booking_types:
            missing.append("At least one booking type")
        
        # Check availability
        has_availability = await self._check_availability(workspace_id)
        if not has_availability:
            missing.append("Availability schedule")
        
        return missing
    
    async def _get_workspace_integrations(self, workspace_id: str) -> List[Dict[str, Any]]:
        """Get workspace integrations"""
        response = (
            self.supabase.table("integrations")
            .select("*")
            .eq("workspace_id", workspace_id)
            .eq("status", "active")
            .execute()
        )
        return response.data
    
    async def _get_booking_types(self, workspace_id: str) -> List[Dict[str, Any]]:
        """Get workspace booking types"""
        response = (
            self.supabase.table("booking_types")
            .select("*")
            .eq("workspace_id", workspace_id)
            .eq("is_active", True)
            .execute()
        )
        return response.data
    
    async def _check_availability(self, workspace_id: str) -> bool:
        """Check if workspace has availability defined"""
        response = (
            self.supabase.table("availability_slots")
            .select("id")
            .eq("workspace_id", workspace_id)
            .limit(1)
            .execute()
        )
        return len(response.data) > 0
