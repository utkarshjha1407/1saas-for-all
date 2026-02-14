"""Inventory endpoints"""
from fastapi import APIRouter, Depends
from typing import List
from supabase import Client

from app.db.supabase_client import get_supabase
from app.schemas.inventory import (
    InventoryItemCreate,
    InventoryItemUpdate,
    InventoryItemResponse,
    InventoryUsageCreate,
    InventoryUsageResponse,
)
from app.schemas.auth import TokenData
from app.core.security import require_staff_or_owner, require_owner
from app.services.base_service import BaseService

router = APIRouter()


@router.post("", response_model=InventoryItemResponse)
async def create_inventory_item(
    item_data: InventoryItemCreate,
    current_user: TokenData = Depends(require_owner),
    supabase: Client = Depends(get_supabase)
):
    """Create inventory item"""
    service = BaseService(supabase, "inventory_items")
    item = await service.create({
        **item_data.model_dump(),
        "workspace_id": current_user.workspace_id,
        "is_low_stock": item_data.quantity <= item_data.low_stock_threshold
    })
    return InventoryItemResponse(**item)


@router.get("", response_model=List[InventoryItemResponse])
async def get_inventory_items(
    current_user: TokenData = Depends(require_staff_or_owner),
    supabase: Client = Depends(get_supabase)
):
    """Get all inventory items"""
    service = BaseService(supabase, "inventory_items")
    items = await service.get_all({"workspace_id": current_user.workspace_id})
    return [InventoryItemResponse(**i) for i in items]


@router.get("/low-stock", response_model=List[InventoryItemResponse])
async def get_low_stock_items(
    current_user: TokenData = Depends(require_staff_or_owner),
    supabase: Client = Depends(get_supabase)
):
    """Get low stock items"""
    service = BaseService(supabase, "inventory_items")
    items = await service.get_all({
        "workspace_id": current_user.workspace_id,
        "is_low_stock": True
    })
    return [InventoryItemResponse(**i) for i in items]


@router.patch("/{item_id}", response_model=InventoryItemResponse)
async def update_inventory_item(
    item_id: str,
    item_data: InventoryItemUpdate,
    current_user: TokenData = Depends(require_staff_or_owner),
    supabase: Client = Depends(get_supabase)
):
    """Update inventory item"""
    service = BaseService(supabase, "inventory_items")
    item = await service.update(item_id, item_data.model_dump(exclude_unset=True))
    return InventoryItemResponse(**item)


@router.post("/usage", response_model=InventoryUsageResponse)
async def record_inventory_usage(
    usage_data: InventoryUsageCreate,
    current_user: TokenData = Depends(require_staff_or_owner),
    supabase: Client = Depends(get_supabase)
):
    """Record inventory usage"""
    service = BaseService(supabase, "inventory_usage")
    usage = await service.create(usage_data.model_dump())
    
    # Update inventory quantity
    item_service = BaseService(supabase, "inventory_items")
    item = await item_service.get_by_id(usage_data.inventory_item_id)
    new_quantity = item["quantity"] - usage_data.quantity_used
    await item_service.update(usage_data.inventory_item_id, {
        "quantity": new_quantity,
        "is_low_stock": new_quantity <= item["low_stock_threshold"]
    })
    
    return InventoryUsageResponse(**usage)
