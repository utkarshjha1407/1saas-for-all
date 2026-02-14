"""Inventory schemas"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class InventoryItemCreate(BaseModel):
    """Create inventory item schema"""
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    quantity: int = Field(..., ge=0)
    low_stock_threshold: int = Field(..., ge=0)
    unit: str = Field(default="unit")


class InventoryItemUpdate(BaseModel):
    """Update inventory item schema"""
    name: Optional[str] = None
    description: Optional[str] = None
    quantity: Optional[int] = Field(None, ge=0)
    low_stock_threshold: Optional[int] = Field(None, ge=0)
    unit: Optional[str] = None


class InventoryItemResponse(BaseModel):
    """Inventory item response schema"""
    id: str
    workspace_id: str
    name: str
    description: Optional[str]
    quantity: int
    low_stock_threshold: int
    unit: str
    is_low_stock: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class InventoryUsageCreate(BaseModel):
    """Create inventory usage schema"""
    inventory_item_id: str
    booking_id: str
    quantity_used: int = Field(..., gt=0)
    notes: Optional[str] = None


class InventoryUsageResponse(BaseModel):
    """Inventory usage response schema"""
    id: str
    inventory_item_id: str
    booking_id: str
    quantity_used: int
    notes: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True
