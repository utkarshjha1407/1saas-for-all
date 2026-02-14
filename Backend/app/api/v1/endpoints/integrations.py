"""Integration endpoints"""
from fastapi import APIRouter, Depends
from typing import List, Dict, Any
from supabase import Client

from app.db.supabase_client import get_supabase
from app.schemas.auth import TokenData
from app.core.security import require_owner
from app.services.base_service import BaseService
from app.models.enums import IntegrationProvider, IntegrationStatus

router = APIRouter()


@router.post("")
async def create_integration(
    provider: IntegrationProvider,
    config: Dict[str, Any],
    current_user: TokenData = Depends(require_owner),
    supabase: Client = Depends(get_supabase)
):
    """Create integration"""
    service = BaseService(supabase, "integrations")
    integration = await service.create({
        "workspace_id": current_user.workspace_id,
        "provider": provider.value,
        "config": config,
        "status": IntegrationStatus.ACTIVE.value
    })
    return integration


@router.get("")
async def get_integrations(
    current_user: TokenData = Depends(require_owner),
    supabase: Client = Depends(get_supabase)
):
    """Get all integrations"""
    service = BaseService(supabase, "integrations")
    integrations = await service.get_all({"workspace_id": current_user.workspace_id})
    return integrations


@router.delete("/{integration_id}")
async def delete_integration(
    integration_id: str,
    current_user: TokenData = Depends(require_owner),
    supabase: Client = Depends(get_supabase)
):
    """Delete integration"""
    service = BaseService(supabase, "integrations")
    await service.delete(integration_id)
    return {"success": True}
