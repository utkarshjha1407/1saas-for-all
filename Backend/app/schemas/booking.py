"""Booking schemas"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime, time
from app.models.enums import BookingStatus


class BookingTypeCreate(BaseModel):
    """Create booking type schema"""
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    duration_minutes: int = Field(..., gt=0)
    location: Optional[str] = None
    is_active: bool = True


class AvailabilitySlot(BaseModel):
    """Availability slot schema"""
    day_of_week: int = Field(..., ge=0, le=6)  # 0=Monday, 6=Sunday
    start_time: time
    end_time: time


class BookingTypeResponse(BaseModel):
    """Booking type response schema"""
    id: str
    workspace_id: str
    name: str
    description: Optional[str]
    duration_minutes: int
    location: Optional[str]
    is_active: bool
    availability_slots: List[AvailabilitySlot]
    created_at: datetime
    
    class Config:
        from_attributes = True


class BookingCreate(BaseModel):
    """Create booking schema"""
    booking_type_id: str
    contact_name: str
    contact_email: str
    contact_phone: Optional[str] = None
    scheduled_at: datetime
    notes: Optional[str] = None


class BookingUpdate(BaseModel):
    """Update booking schema"""
    scheduled_at: Optional[datetime] = None
    status: Optional[BookingStatus] = None
    notes: Optional[str] = None


class BookingResponse(BaseModel):
    """Booking response schema"""
    id: str
    workspace_id: str
    booking_type_id: str
    contact_id: str
    scheduled_at: datetime
    status: BookingStatus
    notes: Optional[str]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True
