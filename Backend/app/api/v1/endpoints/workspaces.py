"""Workspace endpoints"""
from fastapi import APIRouter, Depends, status
from supabase import Client

from app.db.supabase_client import get_supabase
from app.schemas.workspace import (
    WorkspaceCreate,
    WorkspaceUpdate,
    WorkspaceResponse,
    OnboardingStatus,
    PublicURLsResponse,
    SlugCheckResponse,
)
from app.schemas.auth import TokenData
from app.core.security import get_current_user, require_owner
from app.services.workspace_service import WorkspaceService
from app.models.enums import OnboardingStep

router = APIRouter()


@router.post("", response_model=WorkspaceResponse, status_code=status.HTTP_201_CREATED)
async def create_workspace(
    workspace_data: WorkspaceCreate,
    current_user: TokenData = Depends(get_current_user),
    supabase: Client = Depends(get_supabase)
):
    """Create new workspace"""
    service = WorkspaceService(supabase)
    workspace = await service.create_workspace(
        workspace_data.model_dump(),
        current_user.user_id
    )
    
    # Update user with workspace_id
    supabase.table("users").update({"workspace_id": workspace["id"]}).eq("id", current_user.user_id).execute()
    
    return WorkspaceResponse(**workspace)


@router.get("/check-slug/{slug}", response_model=SlugCheckResponse)
async def check_slug_availability(
    slug: str,
    supabase: Client = Depends(get_supabase)
):
    """Check if workspace slug is available"""
    service = WorkspaceService(supabase)
    available = await service.check_slug_available(slug)
    
    if not available:
        # Generate suggested slug
        suggested = await service._generate_unique_slug(slug)
        return SlugCheckResponse(available=False, suggested_slug=suggested)
    
    return SlugCheckResponse(available=True)


@router.get("/{workspace_id}", response_model=WorkspaceResponse)
async def get_workspace(
    workspace_id: str,
    current_user: TokenData = Depends(get_current_user),
    supabase: Client = Depends(get_supabase)
):
    """Get workspace details"""
    service = WorkspaceService(supabase)
    workspace = await service.get_by_id(workspace_id)
    return WorkspaceResponse(**workspace)


@router.patch("/{workspace_id}", response_model=WorkspaceResponse)
async def update_workspace(
    workspace_id: str,
    workspace_data: WorkspaceUpdate,
    current_user: TokenData = Depends(require_owner),
    supabase: Client = Depends(get_supabase)
):
    """Update workspace"""
    service = WorkspaceService(supabase)
    workspace = await service.update(workspace_id, workspace_data.model_dump(exclude_unset=True))
    return WorkspaceResponse(**workspace)


@router.get("/{workspace_id}/onboarding", response_model=OnboardingStatus)
async def get_onboarding_status(
    workspace_id: str,
    current_user: TokenData = Depends(get_current_user),
    supabase: Client = Depends(get_supabase)
):
    """Get workspace onboarding status"""
    service = WorkspaceService(supabase)
    status = await service.get_onboarding_status(workspace_id)
    return OnboardingStatus(**status)


@router.get("/{workspace_id}/public-urls", response_model=PublicURLsResponse)
async def get_public_urls(
    workspace_id: str,
    current_user: TokenData = Depends(get_current_user),
    supabase: Client = Depends(get_supabase)
):
    """Get public URLs for workspace"""
    service = WorkspaceService(supabase)
    urls = await service.get_public_urls(workspace_id)
    return PublicURLsResponse(**urls)


@router.post("/{workspace_id}/activate", response_model=WorkspaceResponse)
async def activate_workspace(
    workspace_id: str,
    current_user: TokenData = Depends(require_owner),
    supabase: Client = Depends(get_supabase)
):
    """Activate workspace after completing onboarding"""
    service = WorkspaceService(supabase)
    workspace = await service.activate_workspace(workspace_id)
    return WorkspaceResponse(**workspace)


@router.post("/{workspace_id}/onboarding/step", response_model=WorkspaceResponse)
async def update_onboarding_step(
    workspace_id: str,
    step: OnboardingStep,
    current_user: TokenData = Depends(require_owner),
    supabase: Client = Depends(get_supabase)
):
    """Update onboarding step"""
    service = WorkspaceService(supabase)
    workspace = await service.update_onboarding_step(workspace_id, step)
    return WorkspaceResponse(**workspace)
