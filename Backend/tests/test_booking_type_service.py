"""Unit tests for BookingTypeService"""
import pytest
from datetime import datetime, date, time, timedelta
from unittest.mock import Mock, AsyncMock, MagicMock, patch
from app.services.booking_type_service import BookingTypeService
from app.core.exceptions import ValidationException


@pytest.fixture
def mock_supabase():
    """Mock Supabase client"""
    mock = Mock()
    mock.table = Mock(return_value=mock)
    mock.select = Mock(return_value=mock)
    mock.insert = Mock(return_value=mock)
    mock.update = Mock(return_value=mock)
    mock.delete = Mock(return_value=mock)
    mock.eq = Mock(return_value=mock)
    mock.neq = Mock(return_value=mock)
    mock.gte = Mock(return_value=mock)
    mock.lte = Mock(return_value=mock)
    mock.order = Mock(return_value=mock)
    mock.limit = Mock(return_value=mock)
    mock.single = Mock(return_value=mock)
    mock.execute = Mock()
    return mock


@pytest.fixture
def booking_type_service(mock_supabase):
    """Create BookingTypeService instance with mocked Supabase"""
    return BookingTypeService(mock_supabase)


class TestCreateBookingType:
    """Tests for create_booking_type method"""
    
    @pytest.mark.asyncio
    async def test_create_booking_type_success(self, booking_type_service, mock_supabase):
        """Test successful booking type creation"""
        workspace_id = "workspace-123"
        data = {
            "name": "Initial Consultation",
            "description": "30 minute consultation",
            "duration_minutes": 30,
            "location_type": "video"
        }
        
        expected_result = {
            "id": "booking-type-123",
            "workspace_id": workspace_id,
            **data,
            "is_active": True
        }
        
        # Mock the create method
        with patch.object(booking_type_service, 'create', new_callable=AsyncMock) as mock_create:
            mock_create.return_value = expected_result
            
            result = await booking_type_service.create_booking_type(workspace_id, data)
            
            assert result == expected_result
            mock_create.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_create_booking_type_missing_name(self, booking_type_service):
        """Test creation fails with missing name"""
        data = {
            "duration_minutes": 30,
            "location_type": "video"
        }
        
        with pytest.raises(ValidationException, match="name is required"):
            await booking_type_service.create_booking_type("workspace-123", data)
    
    @pytest.mark.asyncio
    async def test_create_booking_type_invalid_duration(self, booking_type_service):
        """Test creation fails with invalid duration"""
        data = {
            "name": "Test Service",
            "duration_minutes": 0
        }
        
        with pytest.raises(ValidationException, match="Duration must be greater than 0"):
            await booking_type_service.create_booking_type("workspace-123", data)
    
    @pytest.mark.asyncio
    async def test_create_booking_type_duration_too_long(self, booking_type_service):
        """Test creation fails with duration exceeding 8 hours"""
        data = {
            "name": "Test Service",
            "duration_minutes": 500
        }
        
        with pytest.raises(ValidationException, match="Duration cannot exceed 8 hours"):
            await booking_type_service.create_booking_type("workspace-123", data)


class TestGetBookingTypes:
    """Tests for get_booking_types method"""
    
    @pytest.mark.asyncio
    async def test_get_booking_types_all(self, booking_type_service, mock_supabase):
        """Test getting all booking types"""
        workspace_id = "workspace-123"
        expected_data = [
            {"id": "1", "name": "Service 1", "is_active": True},
            {"id": "2", "name": "Service 2", "is_active": False}
        ]
        
        mock_response = Mock()
        mock_response.data = expected_data
        mock_supabase.execute.return_value = mock_response
        
        result = await booking_type_service.get_booking_types(workspace_id)
        
        assert result == expected_data
        mock_supabase.table.assert_called_with("booking_types")
        mock_supabase.eq.assert_any_call("workspace_id", workspace_id)
    
    @pytest.mark.asyncio
    async def test_get_booking_types_active_only(self, booking_type_service, mock_supabase):
        """Test getting only active booking types"""
        workspace_id = "workspace-123"
        expected_data = [
            {"id": "1", "name": "Service 1", "is_active": True}
        ]
        
        mock_response = Mock()
        mock_response.data = expected_data
        mock_supabase.execute.return_value = mock_response
        
        result = await booking_type_service.get_booking_types(workspace_id, active_only=True)
        
        assert result == expected_data
        mock_supabase.eq.assert_any_call("is_active", True)


class TestUpdateBookingType:
    """Tests for update_booking_type method"""
    
    @pytest.mark.asyncio
    async def test_update_booking_type_success(self, booking_type_service):
        """Test successful booking type update"""
        booking_type_id = "booking-type-123"
        data = {"name": "Updated Name"}
        
        expected_result = {"id": booking_type_id, **data}
        
        with patch.object(booking_type_service, 'update', new_callable=AsyncMock) as mock_update:
            mock_update.return_value = expected_result
            
            result = await booking_type_service.update_booking_type(booking_type_id, data)
            
            assert result == expected_result
            mock_update.assert_called_once_with(booking_type_id, data)
    
    @pytest.mark.asyncio
    async def test_update_booking_type_invalid_duration(self, booking_type_service):
        """Test update fails with invalid duration"""
        data = {"duration_minutes": -10}
        
        with pytest.raises(ValidationException):
            await booking_type_service.update_booking_type("booking-type-123", data)


class TestDeleteBookingType:
    """Tests for delete_booking_type method"""
    
    @pytest.mark.asyncio
    async def test_delete_booking_type_soft_delete(self, booking_type_service):
        """Test soft delete sets is_active to False"""
        booking_type_id = "booking-type-123"
        
        with patch.object(booking_type_service, 'update', new_callable=AsyncMock) as mock_update:
            result = await booking_type_service.delete_booking_type(booking_type_id)
            
            assert result is True
            mock_update.assert_called_once_with(booking_type_id, {"is_active": False})


class TestSetAvailability:
    """Tests for set_availability method"""
    
    @pytest.mark.asyncio
    async def test_set_availability_success(self, booking_type_service, mock_supabase):
        """Test successful availability setting"""
        booking_type_id = "booking-type-123"
        slots = [
            {"day_of_week": 1, "start_time": "09:00", "end_time": "17:00"},
            {"day_of_week": 2, "start_time": "09:00", "end_time": "17:00"}
        ]
        
        booking_type = {
            "id": booking_type_id,
            "workspace_id": "workspace-123"
        }
        
        mock_response = Mock()
        mock_response.data = slots
        mock_supabase.execute.return_value = mock_response
        
        with patch.object(booking_type_service, 'get_by_id', new_callable=AsyncMock) as mock_get:
            mock_get.return_value = booking_type
            
            result = await booking_type_service.set_availability(booking_type_id, slots)
            
            assert len(result) == 2
            mock_supabase.table.assert_any_call("availability_slots")
    
    @pytest.mark.asyncio
    async def test_set_availability_empty_slots(self, booking_type_service):
        """Test setting availability with empty slots fails"""
        with pytest.raises(ValidationException, match="At least one availability slot is required"):
            await booking_type_service.set_availability("booking-type-123", [])
    
    @pytest.mark.asyncio
    async def test_set_availability_invalid_day(self, booking_type_service, mock_supabase):
        """Test setting availability with invalid day of week"""
        slots = [{"day_of_week": 7, "start_time": "09:00", "end_time": "17:00"}]
        
        booking_type = {"id": "booking-type-123", "workspace_id": "workspace-123"}
        
        with patch.object(booking_type_service, 'get_by_id', new_callable=AsyncMock) as mock_get:
            mock_get.return_value = booking_type
            
            with pytest.raises(ValidationException, match="Invalid day of week"):
                await booking_type_service.set_availability("booking-type-123", slots)
    
    @pytest.mark.asyncio
    async def test_set_availability_invalid_time_format(self, booking_type_service, mock_supabase):
        """Test setting availability with invalid time format"""
        slots = [{"day_of_week": 1, "start_time": "25:00", "end_time": "17:00"}]
        
        booking_type = {"id": "booking-type-123", "workspace_id": "workspace-123"}
        
        with patch.object(booking_type_service, 'get_by_id', new_callable=AsyncMock) as mock_get:
            mock_get.return_value = booking_type
            
            with pytest.raises(ValidationException, match="Invalid time format"):
                await booking_type_service.set_availability("booking-type-123", slots)
    
    @pytest.mark.asyncio
    async def test_set_availability_start_after_end(self, booking_type_service, mock_supabase):
        """Test setting availability with start time after end time"""
        slots = [{"day_of_week": 1, "start_time": "17:00", "end_time": "09:00"}]
        
        booking_type = {"id": "booking-type-123", "workspace_id": "workspace-123"}
        
        with patch.object(booking_type_service, 'get_by_id', new_callable=AsyncMock) as mock_get:
            mock_get.return_value = booking_type
            
            with pytest.raises(ValidationException, match="Start time must be before end time"):
                await booking_type_service.set_availability("booking-type-123", slots)


class TestGetAvailability:
    """Tests for get_availability method"""
    
    @pytest.mark.asyncio
    async def test_get_availability_success(self, booking_type_service, mock_supabase):
        """Test getting availability slots"""
        booking_type_id = "booking-type-123"
        expected_data = [
            {"id": "1", "day_of_week": 1, "start_time": "09:00", "end_time": "17:00"}
        ]
        
        mock_response = Mock()
        mock_response.data = expected_data
        mock_supabase.execute.return_value = mock_response
        
        result = await booking_type_service.get_availability(booking_type_id)
        
        assert result == expected_data
        mock_supabase.eq.assert_called_with("booking_type_id", booking_type_id)


class TestGetAvailableSlots:
    """Tests for get_available_slots method"""
    
    @pytest.mark.asyncio
    async def test_get_available_slots_invalid_date_format(self, booking_type_service):
        """Test getting slots with invalid date format"""
        with pytest.raises(ValidationException, match="Invalid date format"):
            await booking_type_service.get_available_slots(
                "booking-type-123",
                "2024-13-01",  # Invalid month
                "2024-12-31"
            )
    
    @pytest.mark.asyncio
    async def test_get_available_slots_end_before_start(self, booking_type_service):
        """Test getting slots with end date before start date"""
        with pytest.raises(ValidationException, match="End date must be after start date"):
            await booking_type_service.get_available_slots(
                "booking-type-123",
                "2024-12-31",
                "2024-01-01"
            )
    
    @pytest.mark.asyncio
    async def test_get_available_slots_range_too_large(self, booking_type_service):
        """Test getting slots with date range exceeding 60 days"""
        with pytest.raises(ValidationException, match="Date range cannot exceed 60 days"):
            await booking_type_service.get_available_slots(
                "booking-type-123",
                "2024-01-01",
                "2024-03-15"  # More than 60 days
            )
    
    @pytest.mark.asyncio
    async def test_get_available_slots_booking_type_not_found(self, booking_type_service):
        """Test getting slots for non-existent booking type"""
        with patch.object(booking_type_service, 'get_by_id', new_callable=AsyncMock) as mock_get:
            mock_get.return_value = None
            
            with pytest.raises(ValidationException, match="Booking type not found"):
                await booking_type_service.get_available_slots(
                    "booking-type-123",
                    "2024-01-01",
                    "2024-01-07"
                )


class TestValidationHelpers:
    """Tests for validation helper methods"""
    
    def test_validate_booking_type_data_valid(self, booking_type_service):
        """Test validation passes with valid data"""
        data = {"name": "Test Service", "duration_minutes": 30}
        # Should not raise exception
        booking_type_service._validate_booking_type_data(data)
    
    def test_validate_booking_type_data_missing_name(self, booking_type_service):
        """Test validation fails with missing name"""
        data = {"duration_minutes": 30}
        with pytest.raises(ValidationException, match="name is required"):
            booking_type_service._validate_booking_type_data(data)
    
    def test_validate_booking_type_data_invalid_duration(self, booking_type_service):
        """Test validation fails with invalid duration"""
        data = {"name": "Test", "duration_minutes": 0}
        with pytest.raises(ValidationException, match="Duration must be greater than 0"):
            booking_type_service._validate_booking_type_data(data)
    
    def test_slots_overlap_true(self, booking_type_service):
        """Test overlap detection returns True for overlapping slots"""
        slot1 = {"start_time": "09:00", "end_time": "12:00"}
        slot2 = {"start_time": "11:00", "end_time": "14:00"}
        
        assert booking_type_service._slots_overlap(slot1, slot2) is True
    
    def test_slots_overlap_false(self, booking_type_service):
        """Test overlap detection returns False for non-overlapping slots"""
        slot1 = {"start_time": "09:00", "end_time": "12:00"}
        slot2 = {"start_time": "12:00", "end_time": "15:00"}
        
        assert booking_type_service._slots_overlap(slot1, slot2) is False
    
    def test_slots_overlap_adjacent(self, booking_type_service):
        """Test adjacent slots don't overlap"""
        slot1 = {"start_time": "09:00", "end_time": "10:00"}
        slot2 = {"start_time": "10:00", "end_time": "11:00"}
        
        assert booking_type_service._slots_overlap(slot1, slot2) is False
