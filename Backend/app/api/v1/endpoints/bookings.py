"""Booking endpoints"""
from fastapi import APIRouter, Depends, Query
from typing import List
from datetime import datetime
from supabase import Client

from app.db.supabase_client import get_supabase
from app.schemas.booking import (
    BookingCreate,
    BookingUpdate,
    BookingResponse,
    BookingTypeCreate,
    BookingTypeResponse,
)
from app.schemas.auth import TokenData
from app.core.security import get_current_user, require_staff_or_owner
from app.services.booking_service import BookingService
from app.models.enums import BookingStatus

router = APIRouter()


@router.post("", response_model=BookingResponse)
async def create_booking(
    booking_data: BookingCreate,
    workspace_id: str = Query(...),
    supabase: Client = Depends(get_supabase)
):
    """Create new booking (public endpoint for customers)"""
    service = BookingService(supabase)
    booking = await service.create_booking(workspace_id, booking_data.model_dump())
    return BookingResponse(**booking)


@router.get("", response_model=List[BookingResponse])
async def get_bookings(
    start_date: datetime = Query(None),
    end_date: datetime = Query(None),
    current_user: TokenData = Depends(require_staff_or_owner),
    supabase: Client = Depends(get_supabase)
):
    """Get bookings for workspace"""
    service = BookingService(supabase)
    
    if start_date and end_date:
        bookings = await service.get_bookings_by_date_range(
            current_user.workspace_id, start_date, end_date
        )
    else:
        bookings = await service.get_all({"workspace_id": current_user.workspace_id})
    
    return [BookingResponse(**b) for b in bookings]


@router.get("/today", response_model=List[BookingResponse])
async def get_today_bookings(
    current_user: TokenData = Depends(require_staff_or_owner),
    supabase: Client = Depends(get_supabase)
):
    """Get today's bookings"""
    service = BookingService(supabase)
    bookings = await service.get_today_bookings(current_user.workspace_id)
    return [BookingResponse(**b) for b in bookings]


@router.get("/upcoming", response_model=List[BookingResponse])
async def get_upcoming_bookings(
    days: int = Query(7, ge=1, le=30),
    current_user: TokenData = Depends(require_staff_or_owner),
    supabase: Client = Depends(get_supabase)
):
    """Get upcoming bookings"""
    service = BookingService(supabase)
    bookings = await service.get_upcoming_bookings(current_user.workspace_id, days)
    return [BookingResponse(**b) for b in bookings]


@router.patch("/{booking_id}", response_model=BookingResponse)
async def update_booking(
    booking_id: str,
    booking_data: BookingUpdate,
    current_user: TokenData = Depends(require_staff_or_owner),
    supabase: Client = Depends(get_supabase)
):
    """Update booking"""
    service = BookingService(supabase)
    booking = await service.update(booking_id, booking_data.model_dump(exclude_unset=True))
    return BookingResponse(**booking)


@router.post("/{booking_id}/status", response_model=BookingResponse)
async def update_booking_status(
    booking_id: str,
    status: BookingStatus,
    current_user: TokenData = Depends(require_staff_or_owner),
    supabase: Client = Depends(get_supabase)
):
    """Update booking status"""
    service = BookingService(supabase)
    booking = await service.update_booking_status(booking_id, status)
    return BookingResponse(**booking)
