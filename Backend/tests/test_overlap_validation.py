"""Unit tests for availability overlap validation"""
import pytest
from unittest.mock import Mock, AsyncMock, patch
from app.services.booking_type_service import BookingTypeService
from app.core.exceptions import ValidationException


@pytest.fixture
def booking_type_service():
    """Create BookingTypeService instance"""
    mock_supabase = Mock()
    return BookingTypeService(mock_supabase)


class TestSlotsOverlap:
    """Tests for _slots_overlap method"""
    
    def test_complete_overlap(self, booking_type_service):
        """Test detection of completely overlapping slots"""
        slot1 = {"start_time": "09:00", "end_time": "12:00"}
        slot2 = {"start_time": "09:00", "end_time": "12:00"}
        
        assert booking_type_service._slots_overlap(slot1, slot2) is True
    
    def test_partial_overlap_start(self, booking_type_service):
        """Test detection of partial overlap at start"""
        slot1 = {"start_time": "09:00", "end_time": "12:00"}
        slot2 = {"start_time": "11:00", "end_time": "14:00"}
        
        assert booking_type_service._slots_overlap(slot1, slot2) is True
    
    def test_partial_overlap_end(self, booking_type_service):
        """Test detection of partial overlap at end"""
        slot1 = {"start_time": "11:00", "end_time": "14:00"}
        slot2 = {"start_time": "09:00", "end_time": "12:00"}
        
        assert booking_type_service._slots_overlap(slot1, slot2) is True
    
    def test_one_slot_contains_another(self, booking_type_service):
        """Test detection when one slot completely contains another"""
        slot1 = {"start_time": "09:00", "end_time": "17:00"}
        slot2 = {"start_time": "11:00", "end_time": "14:00"}
        
        assert booking_type_service._slots_overlap(slot1, slot2) is True
    
    def test_no_overlap_before(self, booking_type_service):
        """Test no overlap when slots are separate (first before second)"""
        slot1 = {"start_time": "09:00", "end_time": "11:00"}
        slot2 = {"start_time": "12:00", "end_time": "14:00"}
        
        assert booking_type_service._slots_overlap(slot1, slot2) is False
    
    def test_no_overlap_after(self, booking_type_service):
        """Test no overlap when slots are separate (first after second)"""
        slot1 = {"start_time": "14:00", "end_time": "16:00"}
        slot2 = {"start_time": "09:00", "end_time": "11:00"}
        
        assert booking_type_service._slots_overlap(slot1, slot2) is False
    
    def test_adjacent_slots_no_overlap(self, booking_type_service):
        """Test adjacent slots (end of one equals start of another) don't overlap"""
        slot1 = {"start_time": "09:00", "end_time": "12:00"}
        slot2 = {"start_time": "12:00", "end_time": "15:00"}
        
        assert booking_type_service._slots_overlap(slot1, slot2) is False
    
    def test_one_minute_overlap(self, booking_type_service):
        """Test detection of even one minute overlap"""
        slot1 = {"start_time": "09:00", "end_time": "12:01"}
        slot2 = {"start_time": "12:00", "end_time": "15:00"}
        
        assert booking_type_service._slots_overlap(slot1, slot2) is True


class TestValidateAvailabilitySlots:
    """Tests for _validate_availability_slots method"""
    
    def test_valid_single_slot(self, booking_type_service):
        """Test validation passes with single valid slot"""
        slots = [
            {"day_of_week": 1, "start_time": "09:00", "end_time": "17:00"}
        ]
        
        # Should not raise exception
        booking_type_service._validate_availability_slots(slots)
    
    def test_valid_multiple_slots_different_days(self, booking_type_service):
        """Test validation passes with multiple slots on different days"""
        slots = [
            {"day_of_week": 1, "start_time": "09:00", "end_time": "17:00"},
            {"day_of_week": 2, "start_time": "09:00", "end_time": "17:00"},
            {"day_of_week": 3, "start_time": "09:00", "end_time": "17:00"}
        ]
        
        # Should not raise exception
        booking_type_service._validate_availability_slots(slots)
    
    def test_valid_multiple_slots_same_day_no_overlap(self, booking_type_service):
        """Test validation passes with multiple non-overlapping slots on same day"""
        slots = [
            {"day_of_week": 1, "start_time": "09:00", "end_time": "12:00"},
            {"day_of_week": 1, "start_time": "13:00", "end_time": "17:00"}
        ]
        
        # Should not raise exception
        booking_type_service._validate_availability_slots(slots)
    
    def test_empty_slots_list(self, booking_type_service):
        """Test validation fails with empty slots list"""
        with pytest.raises(ValidationException, match="At least one availability slot is required"):
            booking_type_service._validate_availability_slots([])
    
    def test_invalid_day_of_week_negative(self, booking_type_service):
        """Test validation fails with negative day of week"""
        slots = [
            {"day_of_week": -1, "start_time": "09:00", "end_time": "17:00"}
        ]
        
        with pytest.raises(ValidationException, match="Invalid day of week"):
            booking_type_service._validate_availability_slots(slots)
    
    def test_invalid_day_of_week_too_large(self, booking_type_service):
        """Test validation fails with day of week > 6"""
        slots = [
            {"day_of_week": 7, "start_time": "09:00", "end_time": "17:00"}
        ]
        
        with pytest.raises(ValidationException, match="Invalid day of week"):
            booking_type_service._validate_availability_slots(slots)
    
    def test_invalid_time_format_hours(self, booking_type_service):
        """Test validation fails with invalid hour format"""
        slots = [
            {"day_of_week": 1, "start_time": "25:00", "end_time": "17:00"}
        ]
        
        with pytest.raises(ValidationException, match="Invalid time format"):
            booking_type_service._validate_availability_slots(slots)
    
    def test_invalid_time_format_minutes(self, booking_type_service):
        """Test validation fails with invalid minute format"""
        slots = [
            {"day_of_week": 1, "start_time": "09:60", "end_time": "17:00"}
        ]
        
        with pytest.raises(ValidationException, match="Invalid time format"):
            booking_type_service._validate_availability_slots(slots)
    
    def test_invalid_time_format_string(self, booking_type_service):
        """Test validation fails with non-time string"""
        slots = [
            {"day_of_week": 1, "start_time": "morning", "end_time": "evening"}
        ]
        
        with pytest.raises(ValidationException, match="Invalid time format"):
            booking_type_service._validate_availability_slots(slots)
    
    def test_start_time_after_end_time(self, booking_type_service):
        """Test validation fails when start time is after end time"""
        slots = [
            {"day_of_week": 1, "start_time": "17:00", "end_time": "09:00"}
        ]
        
        with pytest.raises(ValidationException, match="Start time must be before end time"):
            booking_type_service._validate_availability_slots(slots)
    
    def test_start_time_equals_end_time(self, booking_type_service):
        """Test validation fails when start time equals end time"""
        slots = [
            {"day_of_week": 1, "start_time": "09:00", "end_time": "09:00"}
        ]
        
        with pytest.raises(ValidationException, match="Start time must be before end time"):
            booking_type_service._validate_availability_slots(slots)
    
    def test_overlapping_slots_same_day(self, booking_type_service):
        """Test validation fails with overlapping slots on same day"""
        slots = [
            {"day_of_week": 1, "start_time": "09:00", "end_time": "13:00"},
            {"day_of_week": 1, "start_time": "12:00", "end_time": "17:00"}
        ]
        
        with pytest.raises(ValidationException, match="Overlapping time slots on day 1"):
            booking_type_service._validate_availability_slots(slots)
    
    def test_multiple_overlapping_slots_same_day(self, booking_type_service):
        """Test validation fails with multiple overlapping slots"""
        slots = [
            {"day_of_week": 2, "start_time": "09:00", "end_time": "12:00"},
            {"day_of_week": 2, "start_time": "11:00", "end_time": "14:00"},
            {"day_of_week": 2, "start_time": "13:00", "end_time": "17:00"}
        ]
        
        with pytest.raises(ValidationException, match="Overlapping time slots on day 2"):
            booking_type_service._validate_availability_slots(slots)
    
    def test_overlapping_slots_different_days_allowed(self, booking_type_service):
        """Test overlapping times on different days is allowed"""
        slots = [
            {"day_of_week": 1, "start_time": "09:00", "end_time": "17:00"},
            {"day_of_week": 2, "start_time": "09:00", "end_time": "17:00"}
        ]
        
        # Should not raise exception - different days can have same times
        booking_type_service._validate_availability_slots(slots)
    
    def test_adjacent_slots_same_day_allowed(self, booking_type_service):
        """Test adjacent slots (no gap) on same day is allowed"""
        slots = [
            {"day_of_week": 1, "start_time": "09:00", "end_time": "12:00"},
            {"day_of_week": 1, "start_time": "12:00", "end_time": "17:00"}
        ]
        
        # Should not raise exception - adjacent is not overlapping
        booking_type_service._validate_availability_slots(slots)
    
    def test_all_days_of_week_valid(self, booking_type_service):
        """Test all valid days of week (0-6) are accepted"""
        slots = [
            {"day_of_week": 0, "start_time": "09:00", "end_time": "17:00"},
            {"day_of_week": 1, "start_time": "09:00", "end_time": "17:00"},
            {"day_of_week": 2, "start_time": "09:00", "end_time": "17:00"},
            {"day_of_week": 3, "start_time": "09:00", "end_time": "17:00"},
            {"day_of_week": 4, "start_time": "09:00", "end_time": "17:00"},
            {"day_of_week": 5, "start_time": "09:00", "end_time": "17:00"},
            {"day_of_week": 6, "start_time": "09:00", "end_time": "17:00"}
        ]
        
        # Should not raise exception
        booking_type_service._validate_availability_slots(slots)
    
    def test_complex_schedule_no_overlap(self, booking_type_service):
        """Test complex schedule with multiple slots per day, no overlaps"""
        slots = [
            # Monday - morning and afternoon
            {"day_of_week": 0, "start_time": "08:00", "end_time": "12:00"},
            {"day_of_week": 0, "start_time": "13:00", "end_time": "17:00"},
            # Tuesday - split schedule
            {"day_of_week": 1, "start_time": "09:00", "end_time": "11:00"},
            {"day_of_week": 1, "start_time": "14:00", "end_time": "16:00"},
            # Wednesday - full day
            {"day_of_week": 2, "start_time": "08:00", "end_time": "18:00"}
        ]
        
        # Should not raise exception
        booking_type_service._validate_availability_slots(slots)
    
    def test_complex_schedule_with_overlap(self, booking_type_service):
        """Test complex schedule detects overlap among multiple slots"""
        slots = [
            {"day_of_week": 3, "start_time": "08:00", "end_time": "12:00"},
            {"day_of_week": 3, "start_time": "13:00", "end_time": "17:00"},
            {"day_of_week": 3, "start_time": "16:00", "end_time": "19:00"}  # Overlaps with second slot
        ]
        
        with pytest.raises(ValidationException, match="Overlapping time slots on day 3"):
            booking_type_service._validate_availability_slots(slots)


class TestSetAvailabilityOverlapValidation:
    """Integration tests for set_availability with overlap validation"""
    
    @pytest.mark.asyncio
    async def test_set_availability_rejects_overlapping_slots(self, booking_type_service):
        """Test that set_availability rejects overlapping slots"""
        booking_type = {
            "id": "booking-type-123",
            "workspace_id": "workspace-123"
        }
        
        overlapping_slots = [
            {"day_of_week": 1, "start_time": "09:00", "end_time": "13:00"},
            {"day_of_week": 1, "start_time": "12:00", "end_time": "17:00"}
        ]
        
        with patch.object(booking_type_service, 'get_by_id', new_callable=AsyncMock) as mock_get:
            mock_get.return_value = booking_type
            
            with pytest.raises(ValidationException, match="Overlapping time slots"):
                await booking_type_service.set_availability("booking-type-123", overlapping_slots)
    
    @pytest.mark.asyncio
    async def test_set_availability_accepts_non_overlapping_slots(self, booking_type_service):
        """Test that set_availability accepts non-overlapping slots"""
        booking_type = {
            "id": "booking-type-123",
            "workspace_id": "workspace-123"
        }
        
        valid_slots = [
            {"day_of_week": 1, "start_time": "09:00", "end_time": "12:00"},
            {"day_of_week": 1, "start_time": "13:00", "end_time": "17:00"}
        ]
        
        mock_supabase = booking_type_service.supabase
        mock_response = Mock()
        mock_response.data = valid_slots
        mock_supabase.execute.return_value = mock_response
        
        with patch.object(booking_type_service, 'get_by_id', new_callable=AsyncMock) as mock_get:
            mock_get.return_value = booking_type
            
            # Should not raise exception
            result = await booking_type_service.set_availability("booking-type-123", valid_slots)
            
            assert len(result) == 2
