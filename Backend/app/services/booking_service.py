"""Booking service"""
from typing import Dict, Any, List
from datetime import datetime, timedelta
from supabase import Client

from app.services.base_service import BaseService
from app.models.enums import BookingStatus
from app.core.exceptions import ValidationException, ConflictException


class BookingService(BaseService):
    """Booking management service"""
    
    def __init__(self, supabase: Client):
        super().__init__(supabase, "bookings")
    
    async def create_booking(
        self, workspace_id: str, booking_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Create new booking with validation"""
        # Validate booking type exists
        booking_type = await self._get_booking_type(booking_data["booking_type_id"])
        
        # Check availability
        is_available = await self._check_availability(
            workspace_id,
            booking_data["booking_type_id"],
            booking_data["scheduled_at"],
            booking_type["duration_minutes"]
        )
        
        if not is_available:
            raise ConflictException("Selected time slot is not available")
        
        # Create booking
        booking = await self.create({
            **booking_data,
            "workspace_id": workspace_id,
            "status": BookingStatus.PENDING.value,
        })
        
        self.logger.info("booking_created", booking_id=booking["id"])
        return booking
    
    async def get_bookings_by_date_range(
        self, workspace_id: str, start_date: datetime, end_date: datetime
    ) -> List[Dict[str, Any]]:
        """Get bookings within date range"""
        response = (
            self.supabase.table(self.table_name)
            .select("*")
            .eq("workspace_id", workspace_id)
            .gte("scheduled_at", start_date.isoformat())
            .lte("scheduled_at", end_date.isoformat())
            .order("scheduled_at")
            .execute()
        )
        return response.data
    
    async def update_booking_status(
        self, booking_id: str, status: BookingStatus
    ) -> Dict[str, Any]:
        """Update booking status"""
        return await self.update(booking_id, {"status": status.value})
    
    async def get_today_bookings(self, workspace_id: str) -> List[Dict[str, Any]]:
        """Get today's bookings"""
        today = datetime.now().date()
        start = datetime.combine(today, datetime.min.time())
        end = datetime.combine(today, datetime.max.time())
        
        return await self.get_bookings_by_date_range(workspace_id, start, end)
    
    async def get_upcoming_bookings(
        self, workspace_id: str, days: int = 7
    ) -> List[Dict[str, Any]]:
        """Get upcoming bookings"""
        start = datetime.now()
        end = start + timedelta(days=days)
        
        return await self.get_bookings_by_date_range(workspace_id, start, end)
    
    async def _get_booking_type(self, booking_type_id: str) -> Dict[str, Any]:
        """Get booking type details"""
        response = (
            self.supabase.table("booking_types")
            .select("*")
            .eq("id", booking_type_id)
            .eq("is_active", True)
            .execute()
        )
        
        if not response.data:
            raise ValidationException("Invalid or inactive booking type")
        
        return response.data[0]
    
    async def _check_availability(
        self,
        workspace_id: str,
        booking_type_id: str,
        scheduled_at: datetime,
        duration_minutes: int
    ) -> bool:
        """Check if time slot is available"""
        # Check if slot falls within defined availability
        day_of_week = scheduled_at.weekday()
        time_slot = scheduled_at.time()
        
        availability_response = (
            self.supabase.table("availability_slots")
            .select("*")
            .eq("workspace_id", workspace_id)
            .eq("booking_type_id", booking_type_id)
            .eq("day_of_week", day_of_week)
            .execute()
        )
        
        if not availability_response.data:
            return False
        
        # Check for overlapping bookings
        end_time = scheduled_at + timedelta(minutes=duration_minutes)
        
        overlapping_response = (
            self.supabase.table(self.table_name)
            .select("id")
            .eq("workspace_id", workspace_id)
            .eq("booking_type_id", booking_type_id)
            .gte("scheduled_at", scheduled_at.isoformat())
            .lt("scheduled_at", end_time.isoformat())
            .neq("status", BookingStatus.CANCELLED.value)
            .execute()
        )
        
        return len(overlapping_response.data) == 0
