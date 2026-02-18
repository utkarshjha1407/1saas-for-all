"""Tests for role-based access control (RBAC) in booking system"""
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


@pytest.fixture
def other_workspace_owner_token_data():
    """Mock owner token data for different workspace"""
    return TokenData(
        user_id="user-789",
        email="other@example.com",
        role=UserRole.OWNER,
        workspace_id="workspace-456"
    )


class TestOwnerOnlyOperations:
    """Tests for operations that only owners can perform"""
    
    @pytest.mark.asyncio
    async def test_owner_can_create_booking_type(self, owner_token_data):
        """Test that owner can create booking types"""
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
                        headers={"Authorization": "Bearer owner-token"}
                    )
                    
                    assert response.status_code == 201
                    assert mock_auth.called
    
    @pytest.mark.asyncio
    async def test_staff_cannot_create_booking_type(self, staff_token_data):
        """Test that staff cannot create booking types"""
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
                    headers={"Authorization": "Bearer staff-token"}
                )
                
                assert response.status_code == 403
    
    @pytest.mark.asyncio
    async def test_owner_can_update_booking_type(self, owner_token_data):
        """Test that owner can update booking types"""
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
                        headers={"Authorization": "Bearer owner-token"}
                    )
                    
                    assert response.status_code == 200
                    assert mock_auth.called
    
    @pytest.mark.asyncio
    async def test_staff_cannot_update_booking_type(self, staff_token_data):
        """Test that staff cannot update booking types"""
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            update_data = {"name": "New Name"}
            
            with patch("app.core.security.get_current_user") as mock_auth:
                mock_auth.return_value = staff_token_data
                
                response = await client.put(
                    "/api/v1/booking-types/booking-type-123",
                    json=update_data,
                    headers={"Authorization": "Bearer staff-token"}
                )
                
                assert response.status_code == 403
    
    @pytest.mark.asyncio
    async def test_owner_can_delete_booking_type(self, owner_token_data):
        """Test that owner can delete booking types"""
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            existing = {
                "id": "booking-type-123",
                "workspace_id": "workspace-123"
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
                        headers={"Authorization": "Bearer owner-token"}
                    )
                    
                    assert response.status_code == 204
                    assert mock_auth.called
    
    @pytest.mark.asyncio
    async def test_staff_cannot_delete_booking_type(self, staff_token_data):
        """Test that staff cannot delete booking types"""
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            with patch("app.core.security.get_current_user") as mock_auth:
                mock_auth.return_value = staff_token_data
                
                response = await client.delete(
                    "/api/v1/booking-types/booking-type-123",
                    headers={"Authorization": "Bearer staff-token"}
                )
                
                assert response.status_code == 403
    
    @pytest.mark.asyncio
    async def test_owner_can_set_availability(self, owner_token_data):
        """Test that owner can set availability"""
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
                        headers={"Authorization": "Bearer owner-token"}
                    )
                    
                    assert response.status_code == 200
                    assert mock_auth.called
    
    @pytest.mark.asyncio
    async def test_staff_cannot_set_availability(self, staff_token_data):
        """Test that staff cannot set availability"""
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
                    headers={"Authorization": "Bearer staff-token"}
                )
                
                assert response.status_code == 403


class TestStaffReadAccess:
    """Tests for read operations that staff can perform"""
    
    @pytest.mark.asyncio
    async def test_staff_can_list_booking_types(self, staff_token_data):
        """Test that staff can list booking types"""
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
                        headers={"Authorization": "Bearer staff-token"}
                    )
                    
                    assert response.status_code == 200
                    assert mock_auth.called
    
    @pytest.mark.asyncio
    async def test_staff_can_get_booking_type(self, staff_token_data):
        """Test that staff can get specific booking type"""
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            booking_type = {
                "id": "booking-type-123",
                "workspace_id": "workspace-123",
                "name": "Test Service"
            }
            
            with patch("app.api.v1.endpoints.booking_types.require_staff_or_owner") as mock_auth:
                mock_auth.return_value = staff_token_data
                
                with patch("app.api.v1.endpoints.booking_types.BookingTypeService") as mock_service:
                    mock_instance = AsyncMock()
                    mock_instance.get_booking_type.return_value = booking_type
                    mock_service.return_value = mock_instance
                    
                    response = await client.get(
                        "/api/v1/booking-types/booking-type-123",
                        headers={"Authorization": "Bearer staff-token"}
                    )
                    
                    assert response.status_code == 200
                    assert mock_auth.called
    
    @pytest.mark.asyncio
    async def test_staff_can_get_availability(self, staff_token_data):
        """Test that staff can view availability"""
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
                    "end_time": "17:00"
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
                        headers={"Authorization": "Bearer staff-token"}
                    )
                    
                    assert response.status_code == 200
                    assert mock_auth.called
    
    @pytest.mark.asyncio
    async def test_staff_can_get_available_slots(self, staff_token_data):
        """Test that staff can view available slots"""
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
                        headers={"Authorization": "Bearer staff-token"}
                    )
                    
                    assert response.status_code == 200
                    assert mock_auth.called


class TestWorkspaceIsolation:
    """Tests for workspace isolation in RBAC"""
    
    @pytest.mark.asyncio
    async def test_owner_cannot_access_other_workspace_booking_types(
        self, other_workspace_owner_token_data
    ):
        """Test that owner from workspace A cannot access workspace B's booking types"""
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            # Booking type belongs to workspace-123
            booking_type = {
                "id": "booking-type-123",
                "workspace_id": "workspace-123",
                "name": "Test Service"
            }
            
            # User is owner of workspace-456
            with patch("app.api.v1.endpoints.booking_types.require_staff_or_owner") as mock_auth:
                mock_auth.return_value = other_workspace_owner_token_data
                
                with patch("app.api.v1.endpoints.booking_types.BookingTypeService") as mock_service:
                    mock_instance = AsyncMock()
                    mock_instance.get_booking_type.return_value = booking_type
                    mock_service.return_value = mock_instance
                    
                    response = await client.get(
                        "/api/v1/booking-types/booking-type-123",
                        headers={"Authorization": "Bearer other-owner-token"}
                    )
                    
                    # Should be forbidden due to workspace mismatch
                    assert response.status_code == 403
    
    @pytest.mark.asyncio
    async def test_owner_cannot_update_other_workspace_booking_types(
        self, other_workspace_owner_token_data
    ):
        """Test that owner cannot update booking types from other workspace"""
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            booking_type = {
                "id": "booking-type-123",
                "workspace_id": "workspace-123"
            }
            
            update_data = {"name": "Hacked Name"}
            
            with patch("app.api.v1.endpoints.booking_types.require_owner") as mock_auth:
                mock_auth.return_value = other_workspace_owner_token_data
                
                with patch("app.api.v1.endpoints.booking_types.BookingTypeService") as mock_service:
                    mock_instance = AsyncMock()
                    mock_instance.get_booking_type.return_value = booking_type
                    mock_service.return_value = mock_instance
                    
                    response = await client.put(
                        "/api/v1/booking-types/booking-type-123",
                        json=update_data,
                        headers={"Authorization": "Bearer other-owner-token"}
                    )
                    
                    assert response.status_code == 403
    
    @pytest.mark.asyncio
    async def test_staff_cannot_access_other_workspace_booking_types(
        self, staff_token_data
    ):
        """Test that staff from workspace A cannot access workspace B's booking types"""
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            # Booking type belongs to different workspace
            booking_type = {
                "id": "booking-type-123",
                "workspace_id": "workspace-456",
                "name": "Test Service"
            }
            
            # Staff is from workspace-123
            with patch("app.api.v1.endpoints.booking_types.require_staff_or_owner") as mock_auth:
                mock_auth.return_value = staff_token_data
                
                with patch("app.api.v1.endpoints.booking_types.BookingTypeService") as mock_service:
                    mock_instance = AsyncMock()
                    mock_instance.get_booking_type.return_value = booking_type
                    mock_service.return_value = mock_instance
                    
                    response = await client.get(
                        "/api/v1/booking-types/booking-type-123",
                        headers={"Authorization": "Bearer staff-token"}
                    )
                    
                    assert response.status_code == 403


class TestUnauthenticatedAccess:
    """Tests for unauthenticated access attempts"""
    
    @pytest.mark.asyncio
    async def test_unauthenticated_cannot_create_booking_type(self):
        """Test that unauthenticated users cannot create booking types"""
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            booking_type_data = {
                "name": "Test Service",
                "duration_minutes": 30,
                "location_type": "video"
            }
            
            response = await client.post(
                "/api/v1/booking-types",
                json=booking_type_data
            )
            
            assert response.status_code == 401
    
    @pytest.mark.asyncio
    async def test_unauthenticated_cannot_list_booking_types(self):
        """Test that unauthenticated users cannot list booking types"""
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get("/api/v1/booking-types")
            
            assert response.status_code == 401
    
    @pytest.mark.asyncio
    async def test_unauthenticated_cannot_update_booking_type(self):
        """Test that unauthenticated users cannot update booking types"""
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            update_data = {"name": "New Name"}
            
            response = await client.put(
                "/api/v1/booking-types/booking-type-123",
                json=update_data
            )
            
            assert response.status_code == 401
    
    @pytest.mark.asyncio
    async def test_unauthenticated_cannot_delete_booking_type(self):
        """Test that unauthenticated users cannot delete booking types"""
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.delete(
                "/api/v1/booking-types/booking-type-123"
            )
            
            assert response.status_code == 401
    
    @pytest.mark.asyncio
    async def test_unauthenticated_cannot_set_availability(self):
        """Test that unauthenticated users cannot set availability"""
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            slots = [
                {"day_of_week": 1, "start_time": "09:00", "end_time": "17:00"}
            ]
            
            response = await client.post(
                "/api/v1/booking-types/booking-type-123/availability",
                json=slots
            )
            
            assert response.status_code == 401


class TestPublicEndpointAccess:
    """Tests for public endpoint access (no authentication required)"""
    
    @pytest.mark.asyncio
    async def test_public_can_list_booking_types(self):
        """Test that public users can list booking types for a workspace"""
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            workspace_id = "workspace-123"
            
            with patch("app.api.v1.endpoints.public.BookingTypeService") as mock_service:
                mock_instance = AsyncMock()
                mock_instance.get_booking_types.return_value = [
                    {
                        "id": "booking-type-1",
                        "workspace_id": workspace_id,
                        "name": "Public Service",
                        "is_active": True,
                        "duration_minutes": 30,
                        "location_type": "video",
                        "created_at": "2024-01-01T00:00:00"
                    }
                ]
                mock_service.return_value = mock_instance
                
                with patch("app.api.v1.endpoints.public.check_rate_limit"):
                    mock_supabase = Mock()
                    mock_response = Mock()
                    mock_response.data = {"id": workspace_id}
                    mock_supabase.table.return_value.select.return_value.eq.return_value.single.return_value.execute.return_value = mock_response
                    
                    with patch("app.api.v1.endpoints.public.get_supabase", return_value=mock_supabase):
                        response = await client.get(
                            f"/api/v1/public/booking-types/{workspace_id}"
                        )
                        
                        assert response.status_code == 200
    
    @pytest.mark.asyncio
    async def test_public_can_create_booking(self):
        """Test that public users can create bookings"""
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

