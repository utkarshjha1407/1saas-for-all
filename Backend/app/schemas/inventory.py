"""Inventory schemas"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class InventoryItemCreate(BaseModel):
    """Create inventory item schema"""
    name: str = Field(..., min_length=1, max_length=255, description="Item name")
    description: Optional[str] = Field(None, description="Item description")
    quantity: int = Field(..., ge=0, description="Current quantity")
    low_stock_threshold: int = Field(..., ge=0, description="Alert when quantity falls below this")
    unit: str = Field(default="unit", max_length=50, description="Unit of measurement (e.g., box, bottle, unit)")
    booking_type_ids: List[str] = Field(default_factory=list, description="Booking types that use this item")
    quantity_per_booking: int = Field(default=1, ge=1, description="Quantity used per booking")


class InventoryItemUpdate(BaseModel):
    """Update inventory item schema"""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    quantity: Optional[int] = Field(None, ge=0)
    low_stock_threshold: Optional[int] = Field(None, ge=0)
    unit: Optional[str] = Field(None, max_length=50)
    booking_type_ids: Optional[List[str]] = None
    quantity_per_booking: Optional[int] = Field(None, ge=1)


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
    booking_type_ids: List[str]
    quantity_per_booking: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class InventoryUsageCreate(BaseModel):
    """Create inventory usage record"""
    inventory_item_id: str
    booking_id: str
    quantity_used: int = Field(..., ge=1)
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


class InventoryAdjustment(BaseModel):
    """Adjust inventory quantity"""
    adjustment: int = Field(..., description="Positive to add, negative to subtract")
    reason: Optional[str] = Field(None, description="Reason for adjustment")


class InventoryForecast(BaseModel):
    """Inventory usage forecast"""
    item_id: str
    item_name: str
    current_quantity: int
    low_stock_threshold: int
    quantity_per_booking: int
    upcoming_bookings: int
    estimated_usage: int
    days_until_depleted: Optional[int]
    reorder_recommended: bool
