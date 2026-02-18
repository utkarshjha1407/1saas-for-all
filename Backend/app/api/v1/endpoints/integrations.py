"""Integration endpoints"""
from fastapi import APIRouter, Depends, HTTPException
from typing import List, Dict, Any
from supabase import Client
from pydantic import BaseModel

from app.db.supabase_client import get_supabase
from app.schemas.auth import TokenData
from app.core.security import require_owner
from app.services.base_service import BaseService
from app.services.integration_service import IntegrationService
from app.models.enums import IntegrationProvider, IntegrationStatus
from app.core.exceptions import IntegrationException

router = APIRouter()


class IntegrationVerifyRequest(BaseModel):
    """Request model for integration verification"""
    provider: IntegrationProvider
    config: Dict[str, Any]


class IntegrationCreateRequest(BaseModel):
    """Request model for creating integration"""
    provider: IntegrationProvider
    config: Dict[str, Any]


@router.post("/verify")
async def verify_integration(
    request: IntegrationVerifyRequest,
    current_user: TokenData = Depends(require_owner),
    supabase: Client = Depends(get_supabase)
):
    """Verify integration connection before saving"""
    service = IntegrationService(supabase)
    
    try:
        # Determine if email or SMS provider
        if request.provider in [IntegrationProvider.RESEND, IntegrationProvider.SENDGRID]:
            result = await service.verify_email_provider(request.provider, request.config)
        elif request.provider == IntegrationProvider.TWILIO:
            result = await service.verify_sms_provider(request.provider, request.config)
        else:
            raise HTTPException(status_code=400, detail=f"Unsupported provider: {request.provider}")
        
        if not result.get("success"):
            # Log failure
            await service.log_integration_failure(
                current_user.workspace_id,
                request.provider.value,
                result.get("error", "Unknown error")
            )
        
        return result
    except IntegrationException as e:
        await service.log_integration_failure(
            current_user.workspace_id,
            request.provider.value,
            str(e)
        )
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        await service.log_integration_failure(
            current_user.workspace_id,
            request.provider.value,
            str(e)
        )
        raise HTTPException(status_code=500, detail=f"Verification failed: {str(e)}")


@router.post("")
async def create_integration(
    request: IntegrationCreateRequest,
    current_user: TokenData = Depends(require_owner),
    supabase: Client = Depends(get_supabase)
):
    """Create integration after verification"""
    service = IntegrationService(supabase)
    
    try:
        # Verify connection first
        if request.provider in [IntegrationProvider.RESEND, IntegrationProvider.SENDGRID]:
            verification = await service.verify_email_provider(request.provider, request.config)
        elif request.provider == IntegrationProvider.TWILIO:
            verification = await service.verify_sms_provider(request.provider, request.config)
        else:
            raise HTTPException(status_code=400, detail=f"Unsupported provider: {request.provider}")
        
        if not verification.get("success"):
            raise HTTPException(status_code=400, detail=verification.get("message", "Verification failed"))
        
        # Create integration
        integration = await service.create({
            "workspace_id": current_user.workspace_id,
            "provider": request.provider.value,
            "config": request.config,
            "status": IntegrationStatus.ACTIVE.value
        })
        
        return integration
    except IntegrationException as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create integration: {str(e)}")


@router.get("")
async def get_integrations(
    current_user: TokenData = Depends(require_owner),
    supabase: Client = Depends(get_supabase)
):
    """Get all integrations with organized status"""
    service = IntegrationService(supabase)
    integrations = await service.get_workspace_integrations(current_user.workspace_id)
    return integrations


@router.delete("/{integration_id}")
async def delete_integration(
    integration_id: str,
    current_user: TokenData = Depends(require_owner),
    supabase: Client = Depends(get_supabase)
):
    """Delete integration"""
    service = IntegrationService(supabase)
    await service.delete(integration_id)
    return {"success": True}
