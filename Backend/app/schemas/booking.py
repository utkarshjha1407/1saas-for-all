"""Booking schemas"""
from pydantic import BaseModel, Field, field_validator
from typing import Optional, List
from datetime import datetime, time
from app.models.enums import BookingStatus


class BookingTypeCreate(BaseModel):
    """Create booking type schema"""
    name: str = Field(..., min_length=3, max_length=100)
    description: Optional[str] = None
    duration_minutes: int = Field(..., ge=15, le=120)
    location_type: str = Field(..., pattern="^(in-person|phone|video|client-location)$")
    
    @field_validator('duration_minutes')
    @classmethod
    def validate_duration(cls, v: int) -> int:
        """Validate duration is one of the allowed values"""
        allowed = [15, 30, 45, 60, 90, 120]
        if v not in allowed:
            raise ValueError(f"Duration must be one of {allowed}")
        return v


class BookingTypeUpdate(BaseModel):
    """Update booking type schema"""
    name: Optional[str] = Field(None, min_length=3, max_length=100)
    description: Optional[str] = None
    duration_minutes: Optional[int] = Field(None, ge=15, le=120)
    location_type: Optional[str] = Field(None, pattern="^(in-person|phone|video|client-location)$")
    is_active: Optional[bool] = None
    
    @field_validator('duration_minutes')
    @classmethod
    def validate_duration(cls, v: Optional[int]) -> Optional[int]:
        """Validate duration is one of the allowed values"""
        if v is not None:
            allowed = [15, 30, 45, 60, 90, 120]
            if v not in allowed:
                raise ValueError(f"Duration must be one of {allowed}")
        return v


class AvailabilitySlotCreate(BaseModel):
    """Create availability slot schema"""
    day_of_week: int = Field(..., ge=0, le=6, description="0=Sunday, 6=Saturday")
    start_time: str = Field(..., pattern="^([0-1][0-9]|2[0-3]):[0-5][0-9]$")
    end_time: str = Field(..., pattern="^([0-1][0-9]|2[0-3]):[0-5][0-9]$")


class AvailabilitySlotResponse(BaseModel):
    """Availability slot response schema"""
    id: str
    booking_type_id: str
    day_of_week: int
    start_time: str
    end_time: str
    created_at: datetime
    
    class Config:
        from_attributes = True


class TimeSlotResponse(BaseModel):
    """Available time slot response schema"""
    start: datetime
    end: datetime
    available: bool


class BookingTypeResponse(BaseModel):
    """Booking type response schema"""
    id: str
    workspace_id: str
    name: str
    description: Optional[str]
    duration_minutes: int
    location_type: str
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


class PublicBookingCreate(BaseModel):
    """Create public booking schema"""
    workspace_id: str
    booking_type_id: str
    booking_date: str = Field(..., pattern="^\\d{4}-\\d{2}-\\d{2}$")
    start_time: str = Field(..., pattern="^([0-1][0-9]|2[0-3]):[0-5][0-9]$")
    contact_name: str = Field(..., min_length=1, max_length=255)
    contact_email: Optional[str] = None
    contact_phone: Optional[str] = None
    notes: Optional[str] = None


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
