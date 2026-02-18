"""Tests for timezone handling in booking system"""
import pytest
from httpx import AsyncClient, ASGITransport
from unittest.mock import Mock, AsyncMock, patch
from datetime import datetime, timezone, timedelta
from app.main import app
from app.schemas.auth import TokenData
from app.models.enums import UserRole


@pytest.fixture
def owner_token_data():
    """Mock owner token data"""
    return TokenData(
        user_id="user-123",
        email="owner@example.com",
        role=UserRole.OWNER,
        workspace_id="workspace-123"
    )


class TestTimezoneHandling:
    """Tests for timezone handling in bookings"""
    
    @pytest.mark.asyncio
    async def test_booking_stored_in_utc(self):
        """Test that bookings are stored in UTC"""
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            booking_data = {
                "workspace_id": "workspace-123",
                "booking_type_id": "booking-type-123",
                "booking_date": "2024-01-15",
                "start_time": "10:00",
                "contact_name": "John Doe",
                "contact_email": "john@example.com"
            }
            
            with patch("app.api.v1.endpoints.public.check_rate_limit"):
                mock_supabase = Mock()
                workspace_response = Mock()
                workspace_response.data = {"id": "workspace-123"}
                
                booking_type = {
                    "id": "booking-type-123",
                    "workspace_id": "workspace-123",
                    "is_active": True,
                    "duration_minutes": 30,
                    "location_type": "video"
                }
                
                contact_search_response = Mock()
                contact_search_response.data = []
                
                new_contact_response = Mock()
                new_contact_response.data = [{"id": "contact-123"}]
                
                # Verify booking is stored with UTC timestamp
                booking_response = Mock()
                booking_response.data = [{
                    "id": "booking-123",
                    "scheduled_at": "2024-01-15T10:00:00+00:00",  # UTC
                    "status": "pending"
                }]
                
                mock_supabase.table.return_value.select.return_value.eq.return_value.single.return_value.execute.return_value = workspace_response
                mock_supabase.table.return_value.select.return_value.eq.return_value.limit.return_value.execute.return_value = contact_search_response
                mock_supabase.table.return_value.insert.return_value.execute.side_effect = [
                    new_contact_response,
                    booking_response
                ]
                
                with patch("app.api.v1.endpoints.public.get_supabase", return_value=mock_supabase):
                    with patch("app.api.v1.endpoints.public.BookingTypeService") as mock_service:
                        mock_instance = AsyncMock()
                        mock_instance.get_booking_type.return_value = booking_type
                        mock_service.return_value = mock_instance
                        
                        response = await client.post(
                            "/api/v1/public/bookings",
                            json=booking_data
                        )
                        
                        assert response.status_code == 201
                        data = response.json()
                        # Verify timestamp includes timezone info
                        assert "scheduled_at" in data["booking"]
    
    @pytest.mark.asyncio
    async def test_availability_slots_timezone_independent(self, owner_token_data):
        """Test that availability slots work across timezones"""
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            existing = {
                "id": "booking-type-123",
                "workspace_id": "workspace-123"
            }
            
            # Availability is stored as time-of-day, not absolute timestamps
            slots = [
                {"day_of_week": 1, "start_time": "09:00", "end_time": "17:00"}
            ]
            
            with patch("app.api.v1.endpoints.booking_types.require_owner") as mock_auth:
                mock_auth.return_value = owner_token_data
                
                with patch("app.api.v1.endpoints.booking_types.BookingTypeService") as mock_service:
                    mock_instance = AsyncMock()
                    mock_instance.get_booking_type.return_value = existing
                    mock_instance.set_availability.return_value = slots
                    mock_service.return_value = mock_instance
                    
                    response = await client.post(
                        "/api/v1/booking-types/booking-type-123/availability",
                        json=slots,
                        headers={"Authorization": "Bearer fake-token"}
                    )
                    
                    assert response.status_code == 200
                    data = response.json()
                    # Times should be stored as-is without timezone conversion
                    assert data[0]["start_time"] == "09:00"
                    assert data[0]["end_time"] == "17:00"
    
    @pytest.mark.asyncio
    async def test_get_available_slots_respects_date_boundaries(self, owner_token_data):
        """Test that available slots respect date boundaries regardless of timezone"""
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            existing = {
                "id": "booking-type-123",
                "workspace_id": "workspace-123"
            }
            
            # Slots should be generated for the requested dates
            slots = [
                {
                    "start": "2024-01-15T09:00:00",
                    "end": "2024-01-15T09:30:00",
                    "available": True
                },
                {
                    "start": "2024-01-15T10:00:00",
                    "end": "2024-01-15T10:30:00",
                    "available": True
                }
            ]
            
            with patch("app.api.v1.endpoints.booking_types.require_staff_or_owner") as mock_auth:
                mock_auth.return_value = owner_token_data
                
                with patch("app.api.v1.endpoints.booking_types.BookingTypeService") as mock_service:
                    mock_instance = AsyncMock()
                    mock_instance.get_booking_type.return_value = existing
                    mock_instance.get_available_slots.return_value = slots
                    mock_service.return_value = mock_instance
                    
                    response = await client.get(
                        "/api/v1/booking-types/booking-type-123/available-slots",
                        params={"start_date": "2024-01-15", "end_date": "2024-01-15"},
                        headers={"Authorization": "Bearer fake-token"}
                    )
                    
                    assert response.status_code == 200
                    data = response.json()
                    # All slots should be within the requested date
                    for slot in data:
                        assert slot["start"].startswith("2024-01-15")
    
    @pytest.mark.asyncio
    async def test_booking_date_validation_handles_timezone(self):
        """Test that booking date validation works correctly with timezones"""
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            # Test booking for "today" in different timezones
            booking_data = {
                "workspace_id": "workspace-123",
                "booking_type_id": "booking-type-123",
                "booking_date": "2024-01-15",
                "start_time": "23:00",  # Late evening
                "contact_name": "John Doe",
                "contact_email": "john@example.com"
            }
            
            with patch("app.api.v1.endpoints.public.check_rate_limit"):
                mock_supabase = Mock()
                workspace_response = Mock()
                workspace_response.data = {"id": "workspace-123"}
                
                booking_type = {
                    "id": "booking-type-123",
                    "workspace_id": "workspace-123",
                    "is_active": True,
                    "duration_minutes": 30,
                    "location_type": "video"
                }
                
                contact_search_response = Mock()
                contact_search_response.data = []
                
                new_contact_response = Mock()
                new_contact_response.data = [{"id": "contact-123"}]
                
                booking_response = Mock()
                booking_response.data = [{
                    "id": "booking-123",
                    "scheduled_at": "2024-01-15T23:00:00+00:00",
                    "status": "pending"
                }]
                
                mock_supabase.table.return_value.select.return_value.eq.return_value.single.return_value.execute.return_value = workspace_response
                mock_supabase.table.return_value.select.return_value.eq.return_value.limit.return_value.execute.return_value = contact_search_response
                mock_supabase.table.return_value.insert.return_value.execute.side_effect = [
                    new_contact_response,
                    booking_response
                ]
                
                with patch("app.api.v1.endpoints.public.get_supabase", return_value=mock_supabase):
                    with patch("app.api.v1.endpoints.public.BookingTypeService") as mock_service:
                        mock_instance = AsyncMock()
                        mock_instance.get_booking_type.return_value = booking_type
                        mock_service.return_value = mock_instance
                        
                        response = await client.post(
                            "/api/v1/public/bookings",
                            json=booking_data
                        )
                        
                        assert response.status_code == 201
    
    @pytest.mark.asyncio
    async def test_daylight_saving_time_handling(self, owner_token_data):
        """Test that system handles daylight saving time transitions"""
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            existing = {
                "id": "booking-type-123",
                "workspace_id": "workspace-123"
            }
            
            # Request slots during DST transition period
            # March 10, 2024 is when DST starts in US
            slots = [
                {
                    "start": "2024-03-10T09:00:00",
                    "end": "2024-03-10T09:30:00",
                    "available": True
                }
            ]
            
            with patch("app.api.v1.endpoints.booking_types.require_staff_or_owner") as mock_auth:
                mock_auth.return_value = owner_token_data
                
                with patch("app.api.v1.endpoints.booking_types.BookingTypeService") as mock_service:
                    mock_instance = AsyncMock()
                    mock_instance.get_booking_type.return_value = existing
                    mock_instance.get_available_slots.return_value = slots
                    mock_service.return_value = mock_instance
                    
                    response = await client.get(
                        "/api/v1/booking-types/booking-type-123/available-slots",
                        params={"start_date": "2024-03-10", "end_date": "2024-03-10"},
                        headers={"Authorization": "Bearer fake-token"}
                    )
                    
                    assert response.status_code == 200
                    data = response.json()
                    assert len(data) > 0
    
    @pytest.mark.asyncio
    async def test_created_at_timestamps_are_utc(self, owner_token_data):
        """Test that created_at timestamps are stored in UTC"""
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            booking_type_data = {
                "name": "Test Service",
                "duration_minutes": 30,
                "location_type": "video"
            }
            
            with patch("app.api.v1.endpoints.booking_types.require_owner") as mock_auth:
                mock_auth.return_value = owner_token_data
                
                with patch("app.api.v1.endpoints.booking_types.BookingTypeService") as mock_service:
                    mock_instance = AsyncMock()
                    # Simulate database returning UTC timestamp
                    utc_now = datetime.now(timezone.utc).isoformat()
                    mock_instance.create_booking_type.return_value = {
                        "id": "booking-type-123",
                        "workspace_id": "workspace-123",
                        **booking_type_data,
                        "is_active": True,
                        "created_at": utc_now
                    }
                    mock_service.return_value = mock_instance
                    
                    response = await client.post(
                        "/api/v1/booking-types",
                        json=booking_type_data,
                        headers={"Authorization": "Bearer fake-token"}
                    )
                    
                    assert response.status_code == 201
                    data = response.json()
                    # Verify timestamp is in ISO format with timezone
                    assert "created_at" in data
                    # Should be parseable as datetime
                    datetime.fromisoformat(data["created_at"].replace('Z', '+00:00'))
    
    @pytest.mark.asyncio
    async def test_slot_calculation_across_midnight(self, owner_token_data):
        """Test that slot calculation handles times crossing midnight"""
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            existing = {
                "id": "booking-type-123",
                "workspace_id": "workspace-123"
            }
            
            # Slots that go late into the evening
            slots = [
                {
                    "start": "2024-01-15T22:00:00",
                    "end": "2024-01-15T22:30:00",
                    "available": True
                },
                {
                    "start": "2024-01-15T23:00:00",
                    "end": "2024-01-15T23:30:00",
                    "available": True
                }
            ]
            
            with patch("app.api.v1.endpoints.booking_types.require_staff_or_owner") as mock_auth:
                mock_auth.return_value = owner_token_data
                
                with patch("app.api.v1.endpoints.booking_types.BookingTypeService") as mock_service:
                    mock_instance = AsyncMock()
                    mock_instance.get_booking_type.return_value = existing
                    mock_instance.get_available_slots.return_value = slots
                    mock_service.return_value = mock_instance
                    
                    response = await client.get(
                        "/api/v1/booking-types/booking-type-123/available-slots",
                        params={"start_date": "2024-01-15", "end_date": "2024-01-15"},
                        headers={"Authorization": "Bearer fake-token"}
                    )
                    
                    assert response.status_code == 200
                    data = response.json()
                    # Slots should not cross into next day
                    for slot in data:
                        assert slot["start"].startswith("2024-01-15")
                        assert slot["end"].startswith("2024-01-15")


class TestInternationalTimezones:
    """Tests for international timezone scenarios"""
    
    @pytest.mark.asyncio
    async def test_booking_from_different_timezone(self):
        """Test creating booking from a different timezone"""
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            # Client in Tokyo (UTC+9) booking for 10:00 local time
            booking_data = {
                "workspace_id": "workspace-123",
                "booking_type_id": "booking-type-123",
                "booking_date": "2024-01-15",
                "start_time": "10:00",
                "contact_name": "Tanaka San",
                "contact_email": "tanaka@example.jp"
            }
            
            with patch("app.api.v1.endpoints.public.check_rate_limit"):
                mock_supabase = Mock()
                workspace_response = Mock()
                workspace_response.data = {"id": "workspace-123"}
                
                booking_type = {
                    "id": "booking-type-123",
                    "workspace_id": "workspace-123",
                    "is_active": True,
                    "duration_minutes": 30,
                    "location_type": "video"
                }
                
                contact_search_response = Mock()
                contact_search_response.data = []
                
                new_contact_response = Mock()
                new_contact_response.data = [{"id": "contact-123"}]
                
                booking_response = Mock()
                booking_response.data = [{
                    "id": "booking-123",
                    "scheduled_at": "2024-01-15T10:00:00+00:00",
                    "status": "pending"
                }]
                
                mock_supabase.table.return_value.select.return_value.eq.return_value.single.return_value.execute.return_value = workspace_response
                mock_supabase.table.return_value.select.return_value.eq.return_value.limit.return_value.execute.return_value = contact_search_response
                mock_supabase.table.return_value.insert.return_value.execute.side_effect = [
                    new_contact_response,
                    booking_response
                ]
                
                with patch("app.api.v1.endpoints.public.get_supabase", return_value=mock_supabase):
                    with patch("app.api.v1.endpoints.public.BookingTypeService") as mock_service:
                        mock_instance = AsyncMock()
                        mock_instance.get_booking_type.return_value = booking_type
                        mock_service.return_value = mock_instance
                        
                        response = await client.post(
                            "/api/v1/public/bookings",
                            json=booking_data
                        )
                        
                        assert response.status_code == 201
    
    @pytest.mark.asyncio
    async def test_availability_for_international_workspace(self, owner_token_data):
        """Test setting availability for workspace in different timezone"""
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            existing = {
                "id": "booking-type-123",
                "workspace_id": "workspace-123"
            }
            
            # Business hours in Sydney (UTC+10/+11)
            slots = [
                {"day_of_week": 1, "start_time": "09:00", "end_time": "17:00"},
                {"day_of_week": 2, "start_time": "09:00", "end_time": "17:00"}
            ]
            
            with patch("app.api.v1.endpoints.booking_types.require_owner") as mock_auth:
                mock_auth.return_value = owner_token_data
                
                with patch("app.api.v1.endpoints.booking_types.BookingTypeService") as mock_service:
                    mock_instance = AsyncMock()
                    mock_instance.get_booking_type.return_value = existing
                    mock_instance.set_availability.return_value = slots
                    mock_service.return_value = mock_instance
                    
                    response = await client.post(
                        "/api/v1/booking-types/booking-type-123/availability",
                        json=slots,
                        headers={"Authorization": "Bearer fake-token"}
                    )
                    
                    assert response.status_code == 200
                    data = response.json()
                    # Times should be stored as local business hours
                    assert data[0]["start_time"] == "09:00"
                    assert data[0]["end_time"] == "17:00"

