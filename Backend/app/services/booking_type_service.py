"""Booking type service for managing service types and availability"""
from typing import Dict, Any, List, Optional
from datetime import datetime, time, timedelta, date
from supabase import Client
import structlog

from app.services.base_service import BaseService
from app.core.exceptions import ValidationException

logger = structlog.get_logger()


class BookingTypeService(BaseService):
    """Service for managing booking types and availability"""
    
    def __init__(self, supabase: Client):
        super().__init__(supabase, "booking_types")
        self.supabase = supabase
    
    async def create_booking_type(
        self, 
        workspace_id: str, 
        data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Create booking type with validation"""
        # Validate data
        self._validate_booking_type_data(data)
        
        booking_type_data = {
            "workspace_id": workspace_id,
            "name": data["name"],
            "description": data.get("description"),
            "duration_minutes": data["duration_minutes"],
            "location_type": data.get("location_type", "video"),
            "is_active": data.get("is_active", True),
        }
        
        booking_type = await self.create(booking_type_data)
        logger.info("booking_type_created", booking_type_id=booking_type["id"])
        
        return booking_type
    
    async def get_booking_types(self, workspace_id: str, active_only: bool = False) -> List[Dict[str, Any]]:
        """Get all booking types for workspace"""
        query = self.supabase.table(self.table_name).select("*").eq("workspace_id", workspace_id)
        
        if active_only:
            query = query.eq("is_active", True)
        
        response = query.order("created_at").execute()
        return response.data
    
    async def get_booking_type(self, booking_type_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific booking type by ID"""
        return await self.get_by_id(booking_type_id)
    
    async def update_booking_type(
        self,
        booking_type_id: str,
        data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Update booking type"""
        if "duration_minutes" in data or "name" in data:
            self._validate_booking_type_data({
                "name": data.get("name", "valid"),
                "duration_minutes": data.get("duration_minutes", 30)
            })
        
        return await self.update(booking_type_id, data)
    
    async def delete_booking_type(self, booking_type_id: str) -> bool:
        """Soft delete booking type"""
        await self.update(booking_type_id, {"is_active": False})
        logger.info("booking_type_deleted", booking_type_id=booking_type_id)
        return True
    
    async def get_workspace_booking_types(
        self, 
        workspace_id: str,
        include_inactive: bool = False
    ) -> List[Dict[str, Any]]:
        """Get all booking types for workspace (legacy method)"""
        return await self.get_booking_types(workspace_id, active_only=not include_inactive)
    
    async def set_availability(
        self,
        booking_type_id: str,
        availability_slots: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Set availability slots for booking type"""
        # Validate slots
        self._validate_availability_slots(availability_slots)
        
        # Get booking type to verify it exists
        booking_type = await self.get_by_id(booking_type_id)
        
        # Delete existing availability slots
        self.supabase.table("availability_slots").delete().eq("booking_type_id", booking_type_id).execute()
        
        # Create new slots
        slots_to_insert = []
        for slot in availability_slots:
            slots_to_insert.append({
                "workspace_id": booking_type["workspace_id"],
                "booking_type_id": booking_type_id,
                "day_of_week": slot["day_of_week"],
                "start_time": slot["start_time"],
                "end_time": slot["end_time"],
            })
        
        if slots_to_insert:
            response = self.supabase.table("availability_slots").insert(slots_to_insert).execute()
            logger.info("availability_set", booking_type_id=booking_type_id, slot_count=len(slots_to_insert))
            return response.data
        
        return []
    
    async def get_availability(self, booking_type_id: str) -> List[Dict[str, Any]]:
        """Get availability slots for booking type"""
        response = (
            self.supabase.table("availability_slots")
            .select("*")
            .eq("booking_type_id", booking_type_id)
            .order("day_of_week")
            .order("start_time")
            .execute()
        )
        return response.data
    
    async def get_available_slots(
        self,
        booking_type_id: str,
        start_date: str,
        end_date: str
    ) -> List[Dict[str, Any]]:
        """Get available time slots for a date range"""
        # Parse dates
        try:
            start = datetime.strptime(start_date, "%Y-%m-%d").date()
            end = datetime.strptime(end_date, "%Y-%m-%d").date()
        except ValueError:
            raise ValidationException("Invalid date format. Use YYYY-MM-DD")
        
        if end < start:
            raise ValidationException("End date must be after start date")
        
        if (end - start).days > 60:
            raise ValidationException("Date range cannot exceed 60 days")
        
        # Get booking type
        booking_type = await self.get_by_id(booking_type_id)
        if not booking_type:
            raise ValidationException("Booking type not found")
        
        workspace_id = booking_type["workspace_id"]
        
        # Generate slots for each date
        all_slots = []
        current_date = start
        
        while current_date <= end:
            time_slots = await self.get_available_time_slots(
                booking_type_id=booking_type_id,
                target_date=current_date,
                workspace_id=workspace_id
            )
            
            for time_slot in time_slots:
                slot_datetime = datetime.combine(current_date, datetime.strptime(time_slot, "%H:%M").time())
                end_datetime = slot_datetime + timedelta(minutes=booking_type["duration_minutes"])
                
                all_slots.append({
                    "start": slot_datetime.isoformat(),
                    "end": end_datetime.isoformat(),
                    "available": True
                })
            
            current_date += timedelta(days=1)
        
        return all_slots
    
    async def get_available_time_slots(
        self,
        booking_type_id: str,
        target_date: date,
        workspace_id: str
    ) -> List[str]:
        """Get available time slots for a specific date"""
        # Get booking type
        booking_type = await self.get_by_id(booking_type_id)
        duration_minutes = booking_type["duration_minutes"]
        
        # Get day of week (0=Monday, 6=Sunday)
        day_of_week = target_date.weekday()
        
        # Get availability slots for this day
        availability_response = (
            self.supabase.table("availability_slots")
            .select("*")
            .eq("booking_type_id", booking_type_id)
            .eq("day_of_week", day_of_week)
            .execute()
        )
        
        if not availability_response.data:
            return []
        
        # Get existing bookings for this date
        start_datetime = datetime.combine(target_date, time.min)
        end_datetime = datetime.combine(target_date, time.max)
        
        bookings_response = (
            self.supabase.table("bookings")
            .select("scheduled_at")
            .eq("workspace_id", workspace_id)
            .eq("booking_type_id", booking_type_id)
            .gte("scheduled_at", start_datetime.isoformat())
            .lte("scheduled_at", end_datetime.isoformat())
            .neq("status", "cancelled")
            .execute()
        )
        
        booked_times = set()
        for booking in bookings_response.data:
            booked_time = datetime.fromisoformat(booking["scheduled_at"]).time()
            booked_times.add(booked_time.strftime("%H:%M"))
        
        # Generate available slots
        available_slots = []
        for slot in availability_response.data:
            start_time = datetime.strptime(slot["start_time"], "%H:%M:%S").time()
            end_time = datetime.strptime(slot["end_time"], "%H:%M:%S").time()
            
            current_time = datetime.combine(target_date, start_time)
            slot_end = datetime.combine(target_date, end_time)
            
            while current_time + timedelta(minutes=duration_minutes) <= slot_end:
                time_str = current_time.strftime("%H:%M")
                if time_str not in booked_times:
                    available_slots.append(time_str)
                current_time += timedelta(minutes=duration_minutes)
        
        return sorted(available_slots)
    
    def _validate_booking_type_data(self, data: Dict[str, Any]) -> None:
        """Validate booking type data"""
        if not data.get("name"):
            raise ValidationException("Booking type name is required")
        
        if not data.get("duration_minutes") or data["duration_minutes"] <= 0:
            raise ValidationException("Duration must be greater than 0")
        
        if data["duration_minutes"] > 480:  # 8 hours
            raise ValidationException("Duration cannot exceed 8 hours")
    
    def _validate_availability_slots(self, slots: List[Dict[str, Any]]) -> None:
        """Validate availability slots"""
        if not slots:
            raise ValidationException("At least one availability slot is required")
        
        for slot in slots:
            # Validate day of week
            if slot["day_of_week"] < 0 or slot["day_of_week"] > 6:
                raise ValidationException("Invalid day of week (must be 0-6)")
            
            # Validate times
            try:
                start = datetime.strptime(slot["start_time"], "%H:%M").time()
                end = datetime.strptime(slot["end_time"], "%H:%M").time()
                
                if start >= end:
                    raise ValidationException("Start time must be before end time")
            except ValueError:
                raise ValidationException("Invalid time format (use HH:MM)")
        
        # Check for overlapping slots on same day
        slots_by_day = {}
        for slot in slots:
            day = slot["day_of_week"]
            if day not in slots_by_day:
                slots_by_day[day] = []
            slots_by_day[day].append(slot)
        
        for day, day_slots in slots_by_day.items():
            for i, slot1 in enumerate(day_slots):
                for slot2 in day_slots[i+1:]:
                    if self._slots_overlap(slot1, slot2):
                        raise ValidationException(f"Overlapping time slots on day {day}")
    
    def _slots_overlap(self, slot1: Dict[str, Any], slot2: Dict[str, Any]) -> bool:
        """Check if two time slots overlap"""
        start1 = datetime.strptime(slot1["start_time"], "%H:%M").time()
        end1 = datetime.strptime(slot1["end_time"], "%H:%M").time()
        start2 = datetime.strptime(slot2["start_time"], "%H:%M").time()
        end2 = datetime.strptime(slot2["end_time"], "%H:%M").time()
        
        return start1 < end2 and start2 < end1
