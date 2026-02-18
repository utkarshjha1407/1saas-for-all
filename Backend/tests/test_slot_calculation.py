"""Unit tests for slot calculation algorithm"""
import pytest
from datetime import datetime, date, time, timedelta
from unittest.mock import Mock, AsyncMock, patch
from app.services.booking_type_service import BookingTypeService


@pytest.fixture
def mock_supabase():
    """Mock Supabase client"""
    mock = Mock()
    mock.table = Mock(return_value=mock)
    mock.select = Mock(return_value=mock)
    mock.eq = Mock(return_value=mock)
    mock.neq = Mock(return_value=mock)
    mock.gte = Mock(return_value=mock)
    mock.lte = Mock(return_value=mock)
    mock.execute = Mock()
    return mock


@pytest.fixture
def booking_type_service(mock_supabase):
    """Create BookingTypeService instance"""
    return BookingTypeService(mock_supabase)


class TestGetAvailableTimeSlots:
    """Tests for get_available_time_slots method"""
    
    @pytest.mark.asyncio
    async def test_no_availability_for_day(self, booking_type_service, mock_supabase):
        """Test returns empty list when no availability for the day"""
        booking_type = {
            "id": "booking-type-123",
            "duration_minutes": 30
        }
        target_date = date(2024, 1, 15)  # Monday
        
        # Mock no availability slots
        mock_response = Mock()
        mock_response.data = []
        mock_supabase.execute.return_value = mock_response
        
        with patch.object(booking_type_service, 'get_by_id', new_callable=AsyncMock) as mock_get:
            mock_get.return_value = booking_type
            
            result = await booking_type_service.get_available_time_slots(
                "booking-type-123",
                target_date,
                "workspace-123"
            )
            
            assert result == []
    
    @pytest.mark.asyncio
    async def test_single_availability_slot_no_bookings(self, booking_type_service, mock_supabase):
        """Test generates correct slots with single availability and no bookings"""
        booking_type = {
            "id": "booking-type-123",
            "duration_minutes": 30
        }
        target_date = date(2024, 1, 15)  # Monday (weekday = 0)
        
        # Mock availability: 9:00 - 11:00 (should generate 4 slots: 9:00, 9:30, 10:00, 10:30)
        availability_data = [{
            "id": "avail-1",
            "booking_type_id": "booking-type-123",
            "day_of_week": 0,
            "start_time": "09:00:00",
            "end_time": "11:00:00"
        }]
        
        # Mock no existing bookings
        bookings_data = []
        
        mock_responses = [
            Mock(data=availability_data),  # First call for availability
            Mock(data=bookings_data)        # Second call for bookings
        ]
        mock_supabase.execute.side_effect = mock_responses
        
        with patch.object(booking_type_service, 'get_by_id', new_callable=AsyncMock) as mock_get:
            mock_get.return_value = booking_type
            
            result = await booking_type_service.get_available_time_slots(
                "booking-type-123",
                target_date,
                "workspace-123"
            )
            
            assert len(result) == 4
            assert "09:00" in result
            assert "09:30" in result
            assert "10:00" in result
            assert "10:30" in result
    
    @pytest.mark.asyncio
    async def test_slots_with_existing_bookings(self, booking_type_service, mock_supabase):
        """Test filters out booked time slots"""
        booking_type = {
            "id": "booking-type-123",
            "duration_minutes": 30
        }
        target_date = date(2024, 1, 15)
        
        # Mock availability: 9:00 - 11:00
        availability_data = [{
            "id": "avail-1",
            "booking_type_id": "booking-type-123",
            "day_of_week": 0,
            "start_time": "09:00:00",
            "end_time": "11:00:00"
        }]
        
        # Mock existing booking at 9:30
        bookings_data = [{
            "id": "booking-1",
            "scheduled_at": "2024-01-15T09:30:00"
        }]
        
        mock_responses = [
            Mock(data=availability_data),
            Mock(data=bookings_data)
        ]
        mock_supabase.execute.side_effect = mock_responses
        
        with patch.object(booking_type_service, 'get_by_id', new_callable=AsyncMock) as mock_get:
            mock_get.return_value = booking_type
            
            result = await booking_type_service.get_available_time_slots(
                "booking-type-123",
                target_date,
                "workspace-123"
            )
            
            assert len(result) == 3
            assert "09:00" in result
            assert "09:30" not in result  # Booked
            assert "10:00" in result
            assert "10:30" in result
    
    @pytest.mark.asyncio
    async def test_60_minute_duration_slots(self, booking_type_service, mock_supabase):
        """Test slot generation with 60-minute duration"""
        booking_type = {
            "id": "booking-type-123",
            "duration_minutes": 60
        }
        target_date = date(2024, 1, 15)
        
        # Mock availability: 9:00 - 12:00 (should generate 3 slots: 9:00, 10:00, 11:00)
        availability_data = [{
            "id": "avail-1",
            "booking_type_id": "booking-type-123",
            "day_of_week": 0,
            "start_time": "09:00:00",
            "end_time": "12:00:00"
        }]
        
        bookings_data = []
        
        mock_responses = [
            Mock(data=availability_data),
            Mock(data=bookings_data)
        ]
        mock_supabase.execute.side_effect = mock_responses
        
        with patch.object(booking_type_service, 'get_by_id', new_callable=AsyncMock) as mock_get:
            mock_get.return_value = booking_type
            
            result = await booking_type_service.get_available_time_slots(
                "booking-type-123",
                target_date,
                "workspace-123"
            )
            
            assert len(result) == 3
            assert "09:00" in result
            assert "10:00" in result
            assert "11:00" in result
    
    @pytest.mark.asyncio
    async def test_15_minute_duration_slots(self, booking_type_service, mock_supabase):
        """Test slot generation with 15-minute duration"""
        booking_type = {
            "id": "booking-type-123",
            "duration_minutes": 15
        }
        target_date = date(2024, 1, 15)
        
        # Mock availability: 9:00 - 10:00 (should generate 4 slots)
        availability_data = [{
            "id": "avail-1",
            "booking_type_id": "booking-type-123",
            "day_of_week": 0,
            "start_time": "09:00:00",
            "end_time": "10:00:00"
        }]
        
        bookings_data = []
        
        mock_responses = [
            Mock(data=availability_data),
            Mock(data=bookings_data)
        ]
        mock_supabase.execute.side_effect = mock_responses
        
        with patch.object(booking_type_service, 'get_by_id', new_callable=AsyncMock) as mock_get:
            mock_get.return_value = booking_type
            
            result = await booking_type_service.get_available_time_slots(
                "booking-type-123",
                target_date,
                "workspace-123"
            )
            
            assert len(result) == 4
            assert "09:00" in result
            assert "09:15" in result
            assert "09:30" in result
            assert "09:45" in result
    
    @pytest.mark.asyncio
    async def test_multiple_availability_slots_same_day(self, booking_type_service, mock_supabase):
        """Test slot generation with multiple availability slots on same day"""
        booking_type = {
            "id": "booking-type-123",
            "duration_minutes": 30
        }
        target_date = date(2024, 1, 15)
        
        # Mock availability: 9:00-11:00 and 14:00-16:00
        availability_data = [
            {
                "id": "avail-1",
                "booking_type_id": "booking-type-123",
                "day_of_week": 0,
                "start_time": "09:00:00",
                "end_time": "11:00:00"
            },
            {
                "id": "avail-2",
                "booking_type_id": "booking-type-123",
                "day_of_week": 0,
                "start_time": "14:00:00",
                "end_time": "16:00:00"
            }
        ]
        
        bookings_data = []
        
        mock_responses = [
            Mock(data=availability_data),
            Mock(data=bookings_data)
        ]
        mock_supabase.execute.side_effect = mock_responses
        
        with patch.object(booking_type_service, 'get_by_id', new_callable=AsyncMock) as mock_get:
            mock_get.return_value = booking_type
            
            result = await booking_type_service.get_available_time_slots(
                "booking-type-123",
                target_date,
                "workspace-123"
            )
            
            # Morning: 9:00, 9:30, 10:00, 10:30 (4 slots)
            # Afternoon: 14:00, 14:30, 15:00, 15:30 (4 slots)
            assert len(result) == 8
            assert "09:00" in result
            assert "10:30" in result
            assert "14:00" in result
            assert "15:30" in result
    
    @pytest.mark.asyncio
    async def test_slots_sorted_chronologically(self, booking_type_service, mock_supabase):
        """Test that returned slots are sorted chronologically"""
        booking_type = {
            "id": "booking-type-123",
            "duration_minutes": 30
        }
        target_date = date(2024, 1, 15)
        
        availability_data = [{
            "id": "avail-1",
            "booking_type_id": "booking-type-123",
            "day_of_week": 0,
            "start_time": "09:00:00",
            "end_time": "11:00:00"
        }]
        
        bookings_data = []
        
        mock_responses = [
            Mock(data=availability_data),
            Mock(data=bookings_data)
        ]
        mock_supabase.execute.side_effect = mock_responses
        
        with patch.object(booking_type_service, 'get_by_id', new_callable=AsyncMock) as mock_get:
            mock_get.return_value = booking_type
            
            result = await booking_type_service.get_available_time_slots(
                "booking-type-123",
                target_date,
                "workspace-123"
            )
            
            # Verify slots are in chronological order
            assert result == sorted(result)
    
    @pytest.mark.asyncio
    async def test_no_slots_when_all_booked(self, booking_type_service, mock_supabase):
        """Test returns empty when all slots are booked"""
        booking_type = {
            "id": "booking-type-123",
            "duration_minutes": 30
        }
        target_date = date(2024, 1, 15)
        
        availability_data = [{
            "id": "avail-1",
            "booking_type_id": "booking-type-123",
            "day_of_week": 0,
            "start_time": "09:00:00",
            "end_time": "10:00:00"
        }]
        
        # All slots booked
        bookings_data = [
            {"id": "booking-1", "scheduled_at": "2024-01-15T09:00:00"},
            {"id": "booking-2", "scheduled_at": "2024-01-15T09:30:00"}
        ]
        
        mock_responses = [
            Mock(data=availability_data),
            Mock(data=bookings_data)
        ]
        mock_supabase.execute.side_effect = mock_responses
        
        with patch.object(booking_type_service, 'get_by_id', new_callable=AsyncMock) as mock_get:
            mock_get.return_value = booking_type
            
            result = await booking_type_service.get_available_time_slots(
                "booking-type-123",
                target_date,
                "workspace-123"
            )
            
            assert len(result) == 0


class TestGetAvailableSlotsDateRange:
    """Tests for get_available_slots method with date ranges"""
    
    @pytest.mark.asyncio
    async def test_multiple_days_slot_generation(self, booking_type_service, mock_supabase):
        """Test slot generation across multiple days"""
        booking_type = {
            "id": "booking-type-123",
            "workspace_id": "workspace-123",
            "duration_minutes": 30
        }
        
        # Mock get_by_id
        with patch.object(booking_type_service, 'get_by_id', new_callable=AsyncMock) as mock_get:
            mock_get.return_value = booking_type
            
            # Mock get_available_time_slots to return 2 slots per day
            with patch.object(booking_type_service, 'get_available_time_slots', new_callable=AsyncMock) as mock_slots:
                mock_slots.return_value = ["09:00", "09:30"]
                
                result = await booking_type_service.get_available_slots(
                    "booking-type-123",
                    "2024-01-15",
                    "2024-01-17"  # 3 days
                )
                
                # Should have 6 slots total (2 per day * 3 days)
                assert len(result) == 6
                
                # Verify each slot has required fields
                for slot in result:
                    assert "start" in slot
                    assert "end" in slot
                    assert "available" in slot
                    assert slot["available"] is True
    
    @pytest.mark.asyncio
    async def test_slot_end_time_calculation(self, booking_type_service, mock_supabase):
        """Test that slot end times are calculated correctly based on duration"""
        booking_type = {
            "id": "booking-type-123",
            "workspace_id": "workspace-123",
            "duration_minutes": 45
        }
        
        with patch.object(booking_type_service, 'get_by_id', new_callable=AsyncMock) as mock_get:
            mock_get.return_value = booking_type
            
            with patch.object(booking_type_service, 'get_available_time_slots', new_callable=AsyncMock) as mock_slots:
                mock_slots.return_value = ["10:00"]
                
                result = await booking_type_service.get_available_slots(
                    "booking-type-123",
                    "2024-01-15",
                    "2024-01-15"
                )
                
                assert len(result) == 1
                slot = result[0]
                
                # Parse start and end times
                start_time = datetime.fromisoformat(slot["start"])
                end_time = datetime.fromisoformat(slot["end"])
                
                # Verify duration is 45 minutes
                duration = (end_time - start_time).total_seconds() / 60
                assert duration == 45
