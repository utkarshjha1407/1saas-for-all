"""Booking types endpoints"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from supabase import Client

from app.db.supabase_client import get_supabase
from app.schemas.booking import (
    BookingTypeCreate,
    BookingTypeUpdate,
    BookingTypeResponse,
    AvailabilitySlotCreate,
    AvailabilitySlotResponse,
    TimeSlotResponse
)
from app.schemas.auth import TokenData
from app.core.security import require_owner, require_staff_or_owner
from app.services.booking_type_service import BookingTypeService
from app.core.exceptions import ValidationException
import logging

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("", response_model=BookingTypeResponse, status_code=201)
async def create_booking_type(
    booking_type_data: BookingTypeCreate,
    current_user: TokenData = Depends(require_owner),
    supabase: Client = Depends(get_supabase)
):
    """Create a new booking type (Owner only)"""
    try:
        service = BookingTypeService(supabase)
        booking_type = await service.create_booking_type(
            workspace_id=current_user.workspace_id,
            data=booking_type_data.model_dump()
        )
        return booking_type
    except ValidationException as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error creating booking type: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to create booking type")


@router.get("", response_model=List[BookingTypeResponse])
async def list_booking_types(
    current_user: TokenData = Depends(require_staff_or_owner),
    supabase: Client = Depends(get_supabase)
):
    """List all booking types for the workspace (Staff or Owner)"""
    try:
        service = BookingTypeService(supabase)
        booking_types = await service.get_booking_types(current_user.workspace_id)
        return booking_types
    except Exception as e:
        logger.error(f"Error listing booking types: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to list booking types")


@router.get("/{booking_type_id}", response_model=BookingTypeResponse)
async def get_booking_type(
    booking_type_id: str,
    current_user: TokenData = Depends(require_staff_or_owner),
    supabase: Client = Depends(get_supabase)
):
    """Get a specific booking type (Staff or Owner)"""
    try:
        service = BookingTypeService(supabase)
        booking_type = await service.get_booking_type(booking_type_id)
        
        if not booking_type:
            raise HTTPException(status_code=404, detail="Booking type not found")
        
        # Verify workspace ownership
        if booking_type["workspace_id"] != current_user.workspace_id:
            raise HTTPException(status_code=403, detail="Access denied")
        
        return booking_type
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting booking type: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get booking type")


@router.put("/{booking_type_id}", response_model=BookingTypeResponse)
async def update_booking_type(
    booking_type_id: str,
    booking_type_data: BookingTypeUpdate,
    current_user: TokenData = Depends(require_owner),
    supabase: Client = Depends(get_supabase)
):
    """Update a booking type (Owner only)"""
    try:
        service = BookingTypeService(supabase)
        
        # Verify booking type exists and belongs to workspace
        existing = await service.get_booking_type(booking_type_id)
        if not existing:
            raise HTTPException(status_code=404, detail="Booking type not found")
        
        if existing["workspace_id"] != current_user.workspace_id:
            raise HTTPException(status_code=403, detail="Access denied")
        
        booking_type = await service.update_booking_type(
            booking_type_id=booking_type_id,
            data=booking_type_data.model_dump(exclude_unset=True)
        )
        return booking_type
    except HTTPException:
        raise
    except ValidationException as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error updating booking type: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to update booking type")


@router.delete("/{booking_type_id}", status_code=204)
async def delete_booking_type(
    booking_type_id: str,
    current_user: TokenData = Depends(require_owner),
    supabase: Client = Depends(get_supabase)
):
    """Delete a booking type (soft delete) (Owner only)"""
    try:
        service = BookingTypeService(supabase)
        
        # Verify booking type exists and belongs to workspace
        existing = await service.get_booking_type(booking_type_id)
        if not existing:
            raise HTTPException(status_code=404, detail="Booking type not found")
        
        if existing["workspace_id"] != current_user.workspace_id:
            raise HTTPException(status_code=403, detail="Access denied")
        
        await service.delete_booking_type(booking_type_id)
        return None
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting booking type: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to delete booking type")


@router.post("/{booking_type_id}/availability", response_model=List[AvailabilitySlotResponse])
async def set_availability(
    booking_type_id: str,
    slots: List[AvailabilitySlotCreate],
    current_user: TokenData = Depends(require_owner),
    supabase: Client = Depends(get_supabase)
):
    """Set availability schedule for a booking type (Owner only)"""
    try:
        service = BookingTypeService(supabase)
        
        # Verify booking type exists and belongs to workspace
        existing = await service.get_booking_type(booking_type_id)
        if not existing:
            raise HTTPException(status_code=404, detail="Booking type not found")
        
        if existing["workspace_id"] != current_user.workspace_id:
            raise HTTPException(status_code=403, detail="Access denied")
        
        availability = await service.set_availability(
            booking_type_id=booking_type_id,
            slots=[slot.model_dump() for slot in slots]
        )
        return availability
    except HTTPException:
        raise
    except ValidationException as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error setting availability: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to set availability")


@router.get("/{booking_type_id}/availability", response_model=List[AvailabilitySlotResponse])
async def get_availability(
    booking_type_id: str,
    current_user: TokenData = Depends(require_staff_or_owner),
    supabase: Client = Depends(get_supabase)
):
    """Get availability schedule for a booking type (Staff or Owner)"""
    try:
        service = BookingTypeService(supabase)
        
        # Verify booking type exists and belongs to workspace
        existing = await service.get_booking_type(booking_type_id)
        if not existing:
            raise HTTPException(status_code=404, detail="Booking type not found")
        
        if existing["workspace_id"] != current_user.workspace_id:
            raise HTTPException(status_code=403, detail="Access denied")
        
        availability = await service.get_availability(booking_type_id)
        return availability
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting availability: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get availability")


@router.get("/{booking_type_id}/available-slots", response_model=List[TimeSlotResponse])
async def get_available_slots(
    booking_type_id: str,
    start_date: str = Query(..., description="Start date (YYYY-MM-DD)"),
    end_date: str = Query(..., description="End date (YYYY-MM-DD)"),
    current_user: TokenData = Depends(require_staff_or_owner),
    supabase: Client = Depends(get_supabase)
):
    """Get available time slots for a booking type (Staff or Owner)"""
    try:
        service = BookingTypeService(supabase)
        
        # Verify booking type exists and belongs to workspace
        existing = await service.get_booking_type(booking_type_id)
        if not existing:
            raise HTTPException(status_code=404, detail="Booking type not found")
        
        if existing["workspace_id"] != current_user.workspace_id:
            raise HTTPException(status_code=403, detail="Access denied")
        
        slots = await service.get_available_slots(
            booking_type_id=booking_type_id,
            start_date=start_date,
            end_date=end_date
        )
        return slots
    except HTTPException:
        raise
    except ValidationException as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error getting available slots: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get available slots")
