"""Inventory endpoints"""
from fastapi import APIRouter, Depends, Query, HTTPException, status
from typing import List
from supabase import Client
import structlog

from app.db.supabase_client import get_supabase
from app.schemas.inventory import (
    InventoryItemCreate,
    InventoryItemUpdate,
    InventoryItemResponse,
    InventoryUsageCreate,
    InventoryUsageResponse,
    InventoryAdjustment,
    InventoryForecast,
)
from app.schemas.auth import TokenData
from app.core.security import require_owner, require_staff_or_owner
from app.services.inventory_service import InventoryService

router = APIRouter()
logger = structlog.get_logger()


@router.post("/items", response_model=InventoryItemResponse, status_code=status.HTTP_201_CREATED)
async def create_inventory_item(
    item_data: InventoryItemCreate,
    current_user: TokenData = Depends(require_owner),
    supabase: Client = Depends(get_supabase)
):
    """Create inventory item (Owner only)"""
    try:
        service = InventoryService(supabase)
        item = await service.create_item({
            **item_data.model_dump(),
            "workspace_id": current_user.workspace_id
        })
        return InventoryItemResponse(**item)
        
    except Exception as e:
        logger.error("create_inventory_item_failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create inventory item"
        )


@router.get("/items", response_model=List[InventoryItemResponse])
async def get_inventory_items(
    low_stock_only: bool = Query(False, description="Filter to low stock items only"),
    current_user: TokenData = Depends(require_staff_or_owner),
    supabase: Client = Depends(get_supabase)
):
    """Get inventory items (Staff or Owner)"""
    try:
        service = InventoryService(supabase)
        items = await service.get_items(current_user.workspace_id, low_stock_only)
        return [InventoryItemResponse(**item) for item in items]
        
    except Exception as e:
        logger.error("get_inventory_items_failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get inventory items"
        )


@router.get("/items/{item_id}", response_model=InventoryItemResponse)
async def get_inventory_item(
    item_id: str,
    current_user: TokenData = Depends(require_staff_or_owner),
    supabase: Client = Depends(get_supabase)
):
    """Get single inventory item (Staff or Owner)"""
    try:
        service = InventoryService(supabase)
        item = await service.get_item(item_id)
        
        if not item:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Inventory item not found"
            )
        
        if item["workspace_id"] != current_user.workspace_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )
        
        return InventoryItemResponse(**item)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("get_inventory_item_failed", item_id=item_id, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get inventory item"
        )


@router.put("/items/{item_id}", response_model=InventoryItemResponse)
async def update_inventory_item(
    item_id: str,
    item_data: InventoryItemUpdate,
    current_user: TokenData = Depends(require_owner),
    supabase: Client = Depends(get_supabase)
):
    """Update inventory item (Owner only)"""
    try:
        service = InventoryService(supabase)
        
        # Verify exists and belongs to workspace
        existing = await service.get_item(item_id)
        if not existing:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Inventory item not found"
            )
        
        if existing["workspace_id"] != current_user.workspace_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )
        
        item = await service.update_item(item_id, item_data.model_dump(exclude_unset=True))
        return InventoryItemResponse(**item)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("update_inventory_item_failed", item_id=item_id, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update inventory item"
        )


@router.delete("/items/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_inventory_item(
    item_id: str,
    current_user: TokenData = Depends(require_owner),
    supabase: Client = Depends(get_supabase)
):
    """Delete inventory item (Owner only)"""
    try:
        service = InventoryService(supabase)
        
        # Verify exists and belongs to workspace
        existing = await service.get_item(item_id)
        if not existing:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Inventory item not found"
            )
        
        if existing["workspace_id"] != current_user.workspace_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )
        
        await service.delete_item(item_id)
        return None
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("delete_inventory_item_failed", item_id=item_id, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete inventory item"
        )


@router.post("/items/{item_id}/adjust", response_model=InventoryItemResponse)
async def adjust_inventory_quantity(
    item_id: str,
    adjustment_data: InventoryAdjustment,
    current_user: TokenData = Depends(require_staff_or_owner),
    supabase: Client = Depends(get_supabase)
):
    """Adjust inventory quantity (Staff or Owner)"""
    try:
        service = InventoryService(supabase)
        
        # Verify exists and belongs to workspace
        existing = await service.get_item(item_id)
        if not existing:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Inventory item not found"
            )
        
        if existing["workspace_id"] != current_user.workspace_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )
        
        item = await service.adjust_quantity(
            item_id,
            adjustment_data.adjustment,
            adjustment_data.reason
        )
        return InventoryItemResponse(**item)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("adjust_inventory_failed", item_id=item_id, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to adjust inventory"
        )


@router.get("/items/{item_id}/usage", response_model=List[InventoryUsageResponse])
async def get_usage_history(
    item_id: str,
    limit: int = Query(50, ge=1, le=100),
    current_user: TokenData = Depends(require_staff_or_owner),
    supabase: Client = Depends(get_supabase)
):
    """Get usage history for an item (Staff or Owner)"""
    try:
        service = InventoryService(supabase)
        
        # Verify item belongs to workspace
        item = await service.get_item(item_id)
        if not item:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Inventory item not found"
            )
        
        if item["workspace_id"] != current_user.workspace_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )
        
        usage = await service.get_usage_history(item_id, limit)
        return [InventoryUsageResponse(**u) for u in usage]
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("get_usage_history_failed", item_id=item_id, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get usage history"
        )


@router.get("/forecast", response_model=List[InventoryForecast])
async def get_inventory_forecast(
    days_ahead: int = Query(30, ge=1, le=90, description="Days to forecast ahead"),
    current_user: TokenData = Depends(require_staff_or_owner),
    supabase: Client = Depends(get_supabase)
):
    """Get inventory usage forecast (Staff or Owner)"""
    try:
        service = InventoryService(supabase)
        forecast = await service.get_forecast(current_user.workspace_id, days_ahead)
        return [InventoryForecast(**f) for f in forecast]
        
    except Exception as e:
        logger.error("get_forecast_failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get forecast"
        )


@router.post("/usage", response_model=InventoryUsageResponse, status_code=status.HTTP_201_CREATED)
async def record_inventory_usage(
    usage_data: InventoryUsageCreate,
    current_user: TokenData = Depends(require_staff_or_owner),
    supabase: Client = Depends(get_supabase)
):
    """Record inventory usage (Staff or Owner)"""
    try:
        service = InventoryService(supabase)
        
        # Verify item belongs to workspace
        item = await service.get_item(usage_data.inventory_item_id)
        if not item:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Inventory item not found"
            )
        
        if item["workspace_id"] != current_user.workspace_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )
        
        usage = await service.record_usage(usage_data.model_dump())
        return InventoryUsageResponse(**usage)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("record_usage_failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to record usage"
        )
