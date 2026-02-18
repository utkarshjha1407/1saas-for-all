"""Integration tests for booking type endpoints"""
import pytest
from httpx import AsyncClient, ASGITransport
from unittest.mock import Mock, AsyncMock, patch
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


@pytest.fixture
def staff_token_data():
    """Mock staff token data"""
    return TokenData(
        user_id="user-456",
        email="staff@example.com",
        role=UserRole.STAFF,
        workspace_id="workspace-123"
    )


class TestCreateBookingType:
    """Tests for POST /api/v1/booking-types"""
    
    @pytest.mark.asyncio
    async def test_create_booking_type_as_owner_success(self, owner_token_data):
        """Test owner can create booking type"""
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            booking_type_data = {
                "name": "Initial Consultation",
                "description": "30 minute consultation",
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
                    data = response.json()
                    assert data["name"] == "Initial Consultation"
                    assert data["duration_minutes"] == 30
    
    @pytest.mark.asyncio
    async def test_create_booking_type_as_staff_forbidden(self, staff_token_data):
        """Test staff cannot create booking type"""
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            booking_type_data = {
                "name": "Test Service",
                "duration_minutes": 30,
                "location_type": "video"
            }
            
            with patch("app.core.security.get_current_user") as mock_auth:
                mock_auth.return_value = staff_token_data
                
                response = await client.post(
                    "/api/v1/booking-types",
                    json=booking_type_data,
                    headers={"Authorization": "Bearer fake-token"}
                )
                
                assert response.status_code == 403
    
    @pytest.mark.asyncio
    async def test_create_booking_type_invalid_duration(self, owner_token_data):
        """Test creation fails with invalid duration"""
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            booking_type_data = {
                "name": "Test Service",
                "duration_minutes": 25,  # Not in allowed list
                "location_type": "video"
            }
            
            with patch("app.api.v1.endpoints.booking_types.require_owner") as mock_auth:
                mock_auth.return_value = owner_token_data
                
                response = await client.post(
                    "/api/v1/booking-types",
                    json=booking_type_data,
                    headers={"Authorization": "Bearer fake-token"}
                )
                
                assert response.status_code == 422  # Validation error
    
    @pytest.mark.asyncio
    async def test_create_booking_type_invalid_location(self, owner_token_data):
        """Test creation fails with invalid location type"""
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            booking_type_data = {
                "name": "Test Service",
                "duration_minutes": 30,
                "location_type": "invalid-location"
            }
            
            with patch("app.api.v1.endpoints.booking_types.require_owner") as mock_auth:
                mock_auth.return_value = owner_token_data
                
                response = await client.post(
                    "/api/v1/booking-types",
                    json=booking_type_data,
                    headers={"Authorization": "Bearer fake-token"}
                )
                
                assert response.status_code == 422


class TestListBookingTypes:
    """Tests for GET /api/v1/booking-types"""
    
    @pytest.mark.asyncio
    async def test_list_booking_types_as_owner(self, owner_token_data):
        """Test owner can list booking types"""
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            expected_data = [
                {
                    "id": "1",
                    "workspace_id": "workspace-123",
                    "name": "Service 1",
                    "duration_minutes": 30,
                    "location_type": "video",
                    "is_active": True,
                    "created_at": "2024-01-01T00:00:00"
                }
            ]
            
            with patch("app.api.v1.endpoints.booking_types.require_staff_or_owner") as mock_auth:
                mock_auth.return_value = owner_token_data
                
                with patch("app.api.v1.endpoints.booking_types.BookingTypeService") as mock_service:
                    mock_instance = AsyncMock()
                    mock_instance.get_booking_types.return_value = expected_data
                    mock_service.return_value = mock_instance
                    
                    response = await client.get(
                        "/api/v1/booking-types",
                        headers={"Authorization": "Bearer fake-token"}
                    )
                    
                    assert response.status_code == 200
                    data = response.json()
                    assert len(data) == 1
                    assert data[0]["name"] == "Service 1"
    
    @pytest.mark.asyncio
    async def test_list_booking_types_as_staff(self, staff_token_data):
        """Test staff can list booking types"""
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            expected_data = [
                {
                    "id": "1",
                    "workspace_id": "workspace-123",
                    "name": "Service 1",
                    "duration_minutes": 30,
                    "location_type": "video",
                    "is_active": True,
                    "created_at": "2024-01-01T00:00:00"
                }
            ]
            
            with patch("app.api.v1.endpoints.booking_types.require_staff_or_owner") as mock_auth:
                mock_auth.return_value = staff_token_data
                
                with patch("app.api.v1.endpoints.booking_types.BookingTypeService") as mock_service:
                    mock_instance = AsyncMock()
                    mock_instance.get_booking_types.return_value = expected_data
                    mock_service.return_value = mock_instance
                    
                    response = await client.get(
                        "/api/v1/booking-types",
                        headers={"Authorization": "Bearer fake-token"}
                    )
                    
                    assert response.status_code == 200
                    data = response.json()
                    assert len(data) == 1


class TestGetBookingType:
    """Tests for GET /api/v1/booking-types/{id}"""
    
    @pytest.mark.asyncio
    async def test_get_booking_type_success(self, owner_token_data):
        """Test getting specific booking type"""
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            booking_type = {
                "id": "booking-type-123",
                "workspace_id": "workspace-123",
                "name": "Test Service",
                "duration_minutes": 30,
                "location_type": "video",
                "is_active": True,
                "created_at": "2024-01-01T00:00:00"
            }
            
            with patch("app.api.v1.endpoints.booking_types.require_staff_or_owner") as mock_auth:
                mock_auth.return_value = owner_token_data
                
                with patch("app.api.v1.endpoints.booking_types.BookingTypeService") as mock_service:
                    mock_instance = AsyncMock()
                    mock_instance.get_booking_type.return_value = booking_type
                    mock_service.return_value = mock_instance
                    
                    response = await client.get(
                        "/api/v1/booking-types/booking-type-123",
                        headers={"Authorization": "Bearer fake-token"}
                    )
                    
                    assert response.status_code == 200
                    data = response.json()
                    assert data["id"] == "booking-type-123"
    
    @pytest.mark.asyncio
    async def test_get_booking_type_not_found(self, owner_token_data):
        """Test 404 when booking type doesn't exist"""
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            with patch("app.api.v1.endpoints.booking_types.require_staff_or_owner") as mock_auth:
                mock_auth.return_value = owner_token_data
                
                with patch("app.api.v1.endpoints.booking_types.BookingTypeService") as mock_service:
                    mock_instance = AsyncMock()
                    mock_instance.get_booking_type.return_value = None
                    mock_service.return_value = mock_instance
                    
                    response = await client.get(
                        "/api/v1/booking-types/nonexistent",
                        headers={"Authorization": "Bearer fake-token"}
                    )
                    
                    assert response.status_code == 404
    
    @pytest.mark.asyncio
    async def test_get_booking_type_wrong_workspace(self, owner_token_data):
        """Test 403 when booking type belongs to different workspace"""
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            booking_type = {
                "id": "booking-type-123",
                "workspace_id": "different-workspace",
                "name": "Test Service"
            }
            
            with patch("app.api.v1.endpoints.booking_types.require_staff_or_owner") as mock_auth:
                mock_auth.return_value = owner_token_data
                
                with patch("app.api.v1.endpoints.booking_types.BookingTypeService") as mock_service:
                    mock_instance = AsyncMock()
                    mock_instance.get_booking_type.return_value = booking_type
                    mock_service.return_value = mock_instance
                    
                    response = await client.get(
                        "/api/v1/booking-types/booking-type-123",
                        headers={"Authorization": "Bearer fake-token"}
                    )
                    
                    assert response.status_code == 403


class TestUpdateBookingType:
    """Tests for PUT /api/v1/booking-types/{id}"""
    
    @pytest.mark.asyncio
    async def test_update_booking_type_as_owner(self, owner_token_data):
        """Test owner can update booking type"""
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            existing = {
                "id": "booking-type-123",
                "workspace_id": "workspace-123",
                "name": "Old Name"
            }
            
            update_data = {"name": "New Name"}
            
            with patch("app.api.v1.endpoints.booking_types.require_owner") as mock_auth:
                mock_auth.return_value = owner_token_data
                
                with patch("app.api.v1.endpoints.booking_types.BookingTypeService") as mock_service:
                    mock_instance = AsyncMock()
                    mock_instance.get_booking_type.return_value = existing
                    mock_instance.update_booking_type.return_value = {**existing, **update_data}
                    mock_service.return_value = mock_instance
                    
                    response = await client.put(
                        "/api/v1/booking-types/booking-type-123",
                        json=update_data,
                        headers={"Authorization": "Bearer fake-token"}
                    )
                    
                    assert response.status_code == 200
                    data = response.json()
                    assert data["name"] == "New Name"
    
    @pytest.mark.asyncio
    async def test_update_booking_type_as_staff_forbidden(self, staff_token_data):
        """Test staff cannot update booking type"""
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            update_data = {"name": "New Name"}
            
            with patch("app.core.security.get_current_user") as mock_auth:
                mock_auth.return_value = staff_token_data
                
                response = await client.put(
                    "/api/v1/booking-types/booking-type-123",
                    json=update_data,
                    headers={"Authorization": "Bearer fake-token"}
                )
                
                assert response.status_code == 403


class TestDeleteBookingType:
    """Tests for DELETE /api/v1/booking-types/{id}"""
    
    @pytest.mark.asyncio
    async def test_delete_booking_type_as_owner(self, owner_token_data):
        """Test owner can delete booking type"""
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            existing = {
                "id": "booking-type-123",
                "workspace_id": "workspace-123",
                "name": "Test Service"
            }
            
            with patch("app.api.v1.endpoints.booking_types.require_owner") as mock_auth:
                mock_auth.return_value = owner_token_data
                
                with patch("app.api.v1.endpoints.booking_types.BookingTypeService") as mock_service:
                    mock_instance = AsyncMock()
                    mock_instance.get_booking_type.return_value = existing
                    mock_instance.delete_booking_type.return_value = True
                    mock_service.return_value = mock_instance
                    
                    response = await client.delete(
                        "/api/v1/booking-types/booking-type-123",
                        headers={"Authorization": "Bearer fake-token"}
                    )
                    
                    assert response.status_code == 204
    
    @pytest.mark.asyncio
    async def test_delete_booking_type_as_staff_forbidden(self, staff_token_data):
        """Test staff cannot delete booking type"""
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            with patch("app.core.security.get_current_user") as mock_auth:
                mock_auth.return_value = staff_token_data
                
                response = await client.delete(
                    "/api/v1/booking-types/booking-type-123",
                    headers={"Authorization": "Bearer fake-token"}
                )
                
                assert response.status_code == 403


class TestSetAvailability:
    """Tests for POST /api/v1/booking-types/{id}/availability"""
    
    @pytest.mark.asyncio
    async def test_set_availability_as_owner(self, owner_token_data):
        """Test owner can set availability"""
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
                    mock_instance.set_availability.return_value = slots
                    mock_service.return_value = mock_instance
                    
                    response = await client.post(
                        "/api/v1/booking-types/booking-type-123/availability",
                        json=slots,
                        headers={"Authorization": "Bearer fake-token"}
                    )
                    
                    assert response.status_code == 200
                    data = response.json()
                    assert len(data) == 1
    
    @pytest.mark.asyncio
    async def test_set_availability_as_staff_forbidden(self, staff_token_data):
        """Test staff cannot set availability"""
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            slots = [
                {"day_of_week": 1, "start_time": "09:00", "end_time": "17:00"}
            ]
            
            with patch("app.core.security.get_current_user") as mock_auth:
                mock_auth.return_value = staff_token_data
                
                response = await client.post(
                    "/api/v1/booking-types/booking-type-123/availability",
                    json=slots,
                    headers={"Authorization": "Bearer fake-token"}
                )
                
                assert response.status_code == 403


class TestGetAvailability:
    """Tests for GET /api/v1/booking-types/{id}/availability"""
    
    @pytest.mark.asyncio
    async def test_get_availability_as_staff(self, staff_token_data):
        """Test staff can view availability"""
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            existing = {
                "id": "booking-type-123",
                "workspace_id": "workspace-123"
            }
            
            slots = [
                {
                    "id": "slot-1",
                    "booking_type_id": "booking-type-123",
                    "day_of_week": 1,
                    "start_time": "09:00",
                    "end_time": "17:00",
                    "created_at": "2024-01-01T00:00:00"
                }
            ]
            
            with patch("app.api.v1.endpoints.booking_types.require_staff_or_owner") as mock_auth:
                mock_auth.return_value = staff_token_data
                
                with patch("app.api.v1.endpoints.booking_types.BookingTypeService") as mock_service:
                    mock_instance = AsyncMock()
                    mock_instance.get_booking_type.return_value = existing
                    mock_instance.get_availability.return_value = slots
                    mock_service.return_value = mock_instance
                    
                    response = await client.get(
                        "/api/v1/booking-types/booking-type-123/availability",
                        headers={"Authorization": "Bearer fake-token"}
                    )
                    
                    assert response.status_code == 200
                    data = response.json()
                    assert len(data) == 1


class TestGetAvailableSlots:
    """Tests for GET /api/v1/booking-types/{id}/available-slots"""
    
    @pytest.mark.asyncio
    async def test_get_available_slots_as_staff(self, staff_token_data):
        """Test staff can view available slots"""
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            existing = {
                "id": "booking-type-123",
                "workspace_id": "workspace-123"
            }
            
            slots = [
                {
                    "start": "2024-01-15T09:00:00",
                    "end": "2024-01-15T09:30:00",
                    "available": True
                }
            ]
            
            with patch("app.api.v1.endpoints.booking_types.require_staff_or_owner") as mock_auth:
                mock_auth.return_value = staff_token_data
                
                with patch("app.api.v1.endpoints.booking_types.BookingTypeService") as mock_service:
                    mock_instance = AsyncMock()
                    mock_instance.get_booking_type.return_value = existing
                    mock_instance.get_available_slots.return_value = slots
                    mock_service.return_value = mock_instance
                    
                    response = await client.get(
                        "/api/v1/booking-types/booking-type-123/available-slots",
                        params={"start_date": "2024-01-15", "end_date": "2024-01-17"},
                        headers={"Authorization": "Bearer fake-token"}
                    )
                    
                    assert response.status_code == 200
                    data = response.json()
                    assert len(data) == 1
