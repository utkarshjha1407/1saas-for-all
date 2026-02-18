"""Tests for error handling and edge cases in booking system"""
import pytest
from httpx import AsyncClient, ASGITransport, ASGITransport
from unittest.mock import Mock, AsyncMock, patch
from datetime import datetime, timedelta
from app.main import app
from app.schemas.auth import TokenData
from app.models.enums import UserRole
from app.core.exceptions import ValidationException


@pytest.fixture
def owner_token_data():
    """Mock owner token data"""
    return TokenData(
        user_id="user-123",
        email="owner@example.com",
        role=UserRole.OWNER,
        workspace_id="workspace-123"
    )


@pytest.fixture
def staff_token_data():
    """Mock staff token data"""
    return TokenData(
        user_id="user-456",
        email="staff@example.com",
        role=UserRole.STAFF,
        workspace_id="workspace-123"
    )


class TestDatabaseErrorHandling:
    """Tests for database error handling"""
    
    @pytest.mark.asyncio
    async def test_create_booking_type_database_error(self, owner_token_data):
        """Test handling of database errors during booking type creation"""
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
                    mock_instance.create_booking_type.side_effect = Exception("Database connection failed")
                    mock_service.return_value = mock_instance
                    
                    response = await client.post(
                        "/api/v1/booking-types",
                        json=booking_type_data,
                        headers={"Authorization": "Bearer fake-token"}
                    )
                    
                    assert response.status_code == 500
    
    @pytest.mark.asyncio
    async def test_get_booking_types_database_error(self, owner_token_data):
        """Test handling of database errors when listing booking types"""
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            with patch("app.api.v1.endpoints.booking_types.require_staff_or_owner") as mock_auth:
                mock_auth.return_value = owner_token_data
                
                with patch("app.api.v1.endpoints.booking_types.BookingTypeService") as mock_service:
                    mock_instance = AsyncMock()
                    mock_instance.get_booking_types.side_effect = Exception("Database timeout")
                    mock_service.return_value = mock_instance
                    
                    response = await client.get(
                        "/api/v1/booking-types",
                        headers={"Authorization": "Bearer fake-token"}
                    )
                    
                    assert response.status_code == 500
    
    @pytest.mark.asyncio
    async def test_set_availability_database_error(self, owner_token_data):
        """Test handling of database errors when setting availability"""
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            existing = {
                "id": "booking-type-123",
                "workspace_id": "workspace-123"
            }
            
            slots = [
                {"day_of_week": 1, "start_time": "09:00", "end_time": "17:00"}
            ]
            
            with patch("app.api.v1.endpoints.booking_types.require_owner") as mock_auth:
                mock_auth.return_value = owner_token_data
                
                with patch("app.api.v1.endpoints.booking_types.BookingTypeService") as mock_service:
                    mock_instance = AsyncMock()
                    mock_instance.get_booking_type.return_value = existing
                    mock_instance.set_availability.side_effect = Exception("Transaction failed")
                    mock_service.return_value = mock_instance
                    
                    response = await client.post(
                        "/api/v1/booking-types/booking-type-123/availability",
                        json=slots,
                        headers={"Authorization": "Bearer fake-token"}
                    )
                    
                    assert response.status_code == 500


class TestEdgeCases:
    """Tests for edge cases in booking system"""
    
    @pytest.mark.asyncio
    async def test_create_booking_type_with_very_long_name(self, owner_token_data):
        """Test creating booking type with maximum length name"""
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            booking_type_data = {
                "name": "A" * 255,  # Maximum length
                "duration_minutes": 30,
                "location_type": "video"
            }
            
            with patch("app.api.v1.endpoints.booking_types.require_owner") as mock_auth:
                mock_auth.return_value = owner_token_data
                
                with patch("app.api.v1.endpoints.booking_types.BookingTypeService") as mock_service:
                    mock_instance = AsyncMock()
                    mock_instance.create_booking_type.return_value = {
                        "id": "booking-type-123",
                        "workspace_id": "workspace-123",
                        **booking_type_data,
                        "is_active": True,
                        "created_at": "2024-01-01T00:00:00"
                    }
                    mock_service.return_value = mock_instance
                    
                    response = await client.post(
                        "/api/v1/booking-types",
                        json=booking_type_data,
                        headers={"Authorization": "Bearer fake-token"}
                    )
                    
                    assert response.status_code == 201
    
    @pytest.mark.asyncio
    async def test_create_booking_type_with_empty_description(self, owner_token_data):
        """Test creating booking type with empty description (optional field)"""
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            booking_type_data = {
                "name": "Test Service",
                "description": "",
                "duration_minutes": 30,
                "location_type": "video"
            }
            
            with patch("app.api.v1.endpoints.booking_types.require_owner") as mock_auth:
                mock_auth.return_value = owner_token_data
                
                with patch("app.api.v1.endpoints.booking_types.BookingTypeService") as mock_service:
                    mock_instance = AsyncMock()
                    mock_instance.create_booking_type.return_value = {
                        "id": "booking-type-123",
                        "workspace_id": "workspace-123",
                        **booking_type_data,
                        "is_active": True,
                        "created_at": "2024-01-01T00:00:00"
                    }
                    mock_service.return_value = mock_instance
                    
                    response = await client.post(
                        "/api/v1/booking-types",
                        json=booking_type_data,
                        headers={"Authorization": "Bearer fake-token"}
                    )
                    
                    assert response.status_code == 201
    
    @pytest.mark.asyncio
    async def test_get_available_slots_with_no_availability(self, owner_token_data):
        """Test getting available slots when no availability is set"""
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            existing = {
                "id": "booking-type-123",
                "workspace_id": "workspace-123"
            }
            
            with patch("app.api.v1.endpoints.booking_types.require_staff_or_owner") as mock_auth:
                mock_auth.return_value = owner_token_data
                
                with patch("app.api.v1.endpoints.booking_types.BookingTypeService") as mock_service:
                    mock_instance = AsyncMock()
                    mock_instance.get_booking_type.return_value = existing
                    mock_instance.get_available_slots.return_value = []  # No slots
                    mock_service.return_value = mock_instance
                    
                    response = await client.get(
                        "/api/v1/booking-types/booking-type-123/available-slots",
                        params={"start_date": "2024-01-15", "end_date": "2024-01-17"},
                        headers={"Authorization": "Bearer fake-token"}
                    )
                    
                    assert response.status_code == 200
                    data = response.json()
                    assert len(data) == 0
    
    @pytest.mark.asyncio
    async def test_get_available_slots_with_past_dates(self, owner_token_data):
        """Test getting available slots for past dates"""
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            existing = {
                "id": "booking-type-123",
                "workspace_id": "workspace-123"
            }
            
            with patch("app.api.v1.endpoints.booking_types.require_staff_or_owner") as mock_auth:
                mock_auth.return_value = owner_token_data
                
                with patch("app.api.v1.endpoints.booking_types.BookingTypeService") as mock_service:
                    mock_instance = AsyncMock()
                    mock_instance.get_booking_type.return_value = existing
                    mock_instance.get_available_slots.return_value = []
                    mock_service.return_value = mock_instance
                    
                    response = await client.get(
                        "/api/v1/booking-types/booking-type-123/available-slots",
                        params={"start_date": "2020-01-01", "end_date": "2020-01-03"},
                        headers={"Authorization": "Bearer fake-token"}
                    )
                    
                    assert response.status_code == 200
                    data = response.json()
                    assert len(data) == 0
    
    @pytest.mark.asyncio
    async def test_create_public_booking_with_special_characters_in_name(self):
        """Test creating booking with special characters in contact name"""
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            booking_data = {
                "workspace_id": "workspace-123",
                "booking_type_id": "booking-type-123",
                "booking_date": "2024-01-15",
                "start_time": "10:00",
                "contact_name": "José María O'Brien-Smith",
                "contact_email": "jose@example.com"
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
                new_contact_response.data = [{
                    "id": "contact-123",
                    "name": "José María O'Brien-Smith"
                }]
                
                booking_response = Mock()
                booking_response.data = [{"id": "booking-123", "status": "pending"}]
                
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
    async def test_update_booking_type_with_no_changes(self, owner_token_data):
        """Test updating booking type with empty update data"""
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            existing = {
                "id": "booking-type-123",
                "workspace_id": "workspace-123",
                "name": "Test Service"
            }
            
            update_data = {}  # No changes
            
            with patch("app.api.v1.endpoints.booking_types.require_owner") as mock_auth:
                mock_auth.return_value = owner_token_data
                
                with patch("app.api.v1.endpoints.booking_types.BookingTypeService") as mock_service:
                    mock_instance = AsyncMock()
                    mock_instance.get_booking_type.return_value = existing
                    mock_instance.update_booking_type.return_value = existing
                    mock_service.return_value = mock_instance
                    
                    response = await client.put(
                        "/api/v1/booking-types/booking-type-123",
                        json=update_data,
                        headers={"Authorization": "Bearer fake-token"}
                    )
                    
                    assert response.status_code == 200
    
    @pytest.mark.asyncio
    async def test_delete_nonexistent_booking_type(self, owner_token_data):
        """Test deleting a booking type that doesn't exist"""
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            with patch("app.api.v1.endpoints.booking_types.require_owner") as mock_auth:
                mock_auth.return_value = owner_token_data
                
                with patch("app.api.v1.endpoints.booking_types.BookingTypeService") as mock_service:
                    mock_instance = AsyncMock()
                    mock_instance.get_booking_type.return_value = None
                    mock_service.return_value = mock_instance
                    
                    response = await client.delete(
                        "/api/v1/booking-types/nonexistent",
                        headers={"Authorization": "Bearer fake-token"}
                    )
                    
                    assert response.status_code == 404
    
    @pytest.mark.asyncio
    async def test_set_availability_with_midnight_times(self, owner_token_data):
        """Test setting availability with midnight (00:00) times"""
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            existing = {
                "id": "booking-type-123",
                "workspace_id": "workspace-123"
            }
            
            slots = [
                {"day_of_week": 1, "start_time": "00:00", "end_time": "23:59"}
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


class TestInputValidation:
    """Tests for input validation edge cases"""
    
    @pytest.mark.asyncio
    async def test_create_booking_type_with_null_name(self, owner_token_data):
        """Test creating booking type with null name"""
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            booking_type_data = {
                "name": None,
                "duration_minutes": 30,
                "location_type": "video"
            }
            
            with patch("app.api.v1.endpoints.booking_types.require_owner") as mock_auth:
                mock_auth.return_value = owner_token_data
                
                response = await client.post(
                    "/api/v1/booking-types",
                    json=booking_type_data,
                    headers={"Authorization": "Bearer fake-token"}
                )
                
                assert response.status_code == 422
    
    @pytest.mark.asyncio
    async def test_create_booking_type_with_negative_duration(self, owner_token_data):
        """Test creating booking type with negative duration"""
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            booking_type_data = {
                "name": "Test Service",
                "duration_minutes": -30,
                "location_type": "video"
            }
            
            with patch("app.api.v1.endpoints.booking_types.require_owner") as mock_auth:
                mock_auth.return_value = owner_token_data
                
                response = await client.post(
                    "/api/v1/booking-types",
                    json=booking_type_data,
                    headers={"Authorization": "Bearer fake-token"}
                )
                
                assert response.status_code == 422
    
    @pytest.mark.asyncio
    async def test_create_booking_type_with_zero_duration(self, owner_token_data):
        """Test creating booking type with zero duration"""
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            booking_type_data = {
                "name": "Test Service",
                "duration_minutes": 0,
                "location_type": "video"
            }
            
            with patch("app.api.v1.endpoints.booking_types.require_owner") as mock_auth:
                mock_auth.return_value = owner_token_data
                
                response = await client.post(
                    "/api/v1/booking-types",
                    json=booking_type_data,
                    headers={"Authorization": "Bearer fake-token"}
                )
                
                assert response.status_code == 422
    
    @pytest.mark.asyncio
    async def test_set_availability_with_invalid_json(self, owner_token_data):
        """Test setting availability with malformed JSON"""
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            with patch("app.api.v1.endpoints.booking_types.require_owner") as mock_auth:
                mock_auth.return_value = owner_token_data
                
                response = await client.post(
                    "/api/v1/booking-types/booking-type-123/availability",
                    content="not valid json",
                    headers={
                        "Authorization": "Bearer fake-token",
                        "Content-Type": "application/json"
                    }
                )
                
                assert response.status_code == 422
    
    @pytest.mark.asyncio
    async def test_get_available_slots_with_invalid_date_range(self, owner_token_data):
        """Test getting available slots with end date before start date"""
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            existing = {
                "id": "booking-type-123",
                "workspace_id": "workspace-123"
            }
            
            with patch("app.api.v1.endpoints.booking_types.require_staff_or_owner") as mock_auth:
                mock_auth.return_value = owner_token_data
                
                with patch("app.api.v1.endpoints.booking_types.BookingTypeService") as mock_service:
                    mock_instance = AsyncMock()
                    mock_instance.get_booking_type.return_value = existing
                    mock_instance.get_available_slots.side_effect = ValidationException(
                        "End date must be after start date"
                    )
                    mock_service.return_value = mock_instance
                    
                    response = await client.get(
                        "/api/v1/booking-types/booking-type-123/available-slots",
                        params={"start_date": "2024-01-20", "end_date": "2024-01-15"},
                        headers={"Authorization": "Bearer fake-token"}
                    )
                    
                    assert response.status_code == 400
    
    @pytest.mark.asyncio
    async def test_create_public_booking_with_invalid_email(self):
        """Test creating booking with invalid email format"""
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            booking_data = {
                "workspace_id": "workspace-123",
                "booking_type_id": "booking-type-123",
                "booking_date": "2024-01-15",
                "start_time": "10:00",
                "contact_name": "John Doe",
                "contact_email": "not-an-email"
            }
            
            response = await client.post(
                "/api/v1/public/bookings",
                json=booking_data
            )
            
            assert response.status_code == 422
    
    @pytest.mark.asyncio
    async def test_create_public_booking_with_sql_injection_attempt(self):
        """Test that SQL injection attempts are properly handled"""
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            booking_data = {
                "workspace_id": "workspace-123'; DROP TABLE bookings; --",
                "booking_type_id": "booking-type-123",
                "booking_date": "2024-01-15",
                "start_time": "10:00",
                "contact_name": "John Doe",
                "contact_email": "john@example.com"
            }
            
            with patch("app.api.v1.endpoints.public.check_rate_limit"):
                mock_supabase = Mock()
                workspace_response = Mock()
                workspace_response.data = None  # Workspace not found
                mock_supabase.table.return_value.select.return_value.eq.return_value.single.return_value.execute.return_value = workspace_response
                
                with patch("app.api.v1.endpoints.public.get_supabase", return_value=mock_supabase):
                    response = await client.post(
                        "/api/v1/public/bookings",
                        json=booking_data
                    )
                    
                    # Should fail gracefully, not execute SQL
                    assert response.status_code in [404, 422]


class TestConcurrency:
    """Tests for concurrent operations"""
    
    @pytest.mark.asyncio
    async def test_concurrent_booking_creation(self):
        """Test handling of concurrent booking creation for same slot"""
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
                
                # First booking succeeds
                booking_response = Mock()
                booking_response.data = [{"id": "booking-123", "status": "pending"}]
                
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

