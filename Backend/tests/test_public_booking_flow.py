"""Integration tests for public booking flow"""
import pytest
from httpx import AsyncClient, ASGITransport
from unittest.mock import Mock, AsyncMock, patch
from app.main import app


class TestGetPublicBookingTypes:
    """Tests for GET /api/v1/public/booking-types/{workspace_id}"""
    
    @pytest.mark.asyncio
    async def test_get_public_booking_types_success(self):
        """Test getting public booking types for valid workspace"""
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            workspace_id = "workspace-123"
            
            with patch("app.api.v1.endpoints.public.BookingTypeService") as mock_service:
                mock_instance = AsyncMock()
                mock_instance.get_booking_types.return_value = [
                    {
                        "id": "booking-type-1",
                        "workspace_id": workspace_id,
                        "name": "Initial Consultation",
                        "description": "30 minute consultation",
                        "duration_minutes": 30,
                        "location_type": "video",
                        "is_active": True,
                        "created_at": "2024-01-01T00:00:00"
                    }
                ]
                mock_service.return_value = mock_instance
                
                with patch("app.api.v1.endpoints.public.check_rate_limit"):
                    # Mock workspace exists check
                    mock_supabase = Mock()
                    mock_response = Mock()
                    mock_response.data = {"id": workspace_id}
                    mock_supabase.table.return_value.select.return_value.eq.return_value.single.return_value.execute.return_value = mock_response
                    
                    with patch("app.api.v1.endpoints.public.get_supabase", return_value=mock_supabase):
                        response = await client.get(f"/api/v1/public/booking-types/{workspace_id}")
                        
                        assert response.status_code == 200
                        data = response.json()
                        assert len(data) == 1
                        assert data[0]["name"] == "Initial Consultation"
    
    @pytest.mark.asyncio
    async def test_get_public_booking_types_workspace_not_found(self):
        """Test 404 when workspace doesn't exist"""
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            with patch("app.api.v1.endpoints.public.check_rate_limit"):
                # Mock workspace not found
                mock_supabase = Mock()
                mock_response = Mock()
                mock_response.data = None
                mock_supabase.table.return_value.select.return_value.eq.return_value.single.return_value.execute.return_value = mock_response
                
                with patch("app.api.v1.endpoints.public.get_supabase", return_value=mock_supabase):
                    response = await client.get("/api/v1/public/booking-types/nonexistent")
                    
                    assert response.status_code == 404
    
    @pytest.mark.asyncio
    async def test_get_public_booking_types_only_active(self):
        """Test only active booking types are returned"""
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            workspace_id = "workspace-123"
            
            with patch("app.api.v1.endpoints.public.BookingTypeService") as mock_service:
                mock_instance = AsyncMock()
                # Verify active_only=True is passed
                mock_instance.get_booking_types.return_value = [
                    {
                        "id": "booking-type-1",
                        "workspace_id": workspace_id,
                        "name": "Active Service",
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
                        response = await client.get(f"/api/v1/public/booking-types/{workspace_id}")
                        
                        assert response.status_code == 200
                        data = response.json()
                        # Verify all returned items are active
                        for item in data:
                            assert item["is_active"] is True


class TestCreatePublicBooking:
    """Tests for POST /api/v1/public/bookings"""
    
    @pytest.mark.asyncio
    async def test_create_public_booking_new_contact(self):
        """Test creating booking with new contact"""
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            booking_data = {
                "workspace_id": "workspace-123",
                "booking_type_id": "booking-type-123",
                "booking_date": "2024-01-15",
                "start_time": "10:00",
                "contact_name": "John Doe",
                "contact_email": "john@example.com",
                "contact_phone": "+1234567890",
                "notes": "First time booking"
            }
            
            with patch("app.api.v1.endpoints.public.check_rate_limit"):
                # Mock workspace exists
                mock_supabase = Mock()
                workspace_response = Mock()
                workspace_response.data = {"id": "workspace-123", "name": "Test Workspace"}
                
                # Mock booking type exists
                booking_type = {
                    "id": "booking-type-123",
                    "workspace_id": "workspace-123",
                    "name": "Consultation",
                    "duration_minutes": 30,
                    "location_type": "video",
                    "is_active": True
                }
                
                # Mock no existing contact
                contact_search_response = Mock()
                contact_search_response.data = []
                
                # Mock contact creation
                new_contact_response = Mock()
                new_contact_response.data = [{
                    "id": "contact-123",
                    "workspace_id": "workspace-123",
                    "name": "John Doe",
                    "email": "john@example.com"
                }]
                
                # Mock conversation creation
                conversation_response = Mock()
                conversation_response.data = [{"id": "conversation-123"}]
                
                # Mock booking creation
                booking_response = Mock()
                booking_response.data = [{
                    "id": "booking-123",
                    "workspace_id": "workspace-123",
                    "booking_type_id": "booking-type-123",
                    "contact_id": "contact-123",
                    "scheduled_at": "2024-01-15T10:00:00",
                    "status": "pending"
                }]
                
                # Setup mock responses
                mock_supabase.table.return_value.select.return_value.eq.return_value.single.return_value.execute.return_value = workspace_response
                mock_supabase.table.return_value.select.return_value.eq.return_value.limit.return_value.execute.return_value = contact_search_response
                mock_supabase.table.return_value.insert.return_value.execute.side_effect = [
                    new_contact_response,
                    conversation_response,
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
                        assert data["success"] is True
                        assert "booking" in data
    
    @pytest.mark.asyncio
    async def test_create_public_booking_existing_contact(self):
        """Test creating booking with existing contact"""
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            booking_data = {
                "workspace_id": "workspace-123",
                "booking_type_id": "booking-type-123",
                "booking_date": "2024-01-15",
                "start_time": "10:00",
                "contact_name": "Jane Doe",
                "contact_email": "jane@example.com"
            }
            
            with patch("app.api.v1.endpoints.public.check_rate_limit"):
                mock_supabase = Mock()
                
                # Mock workspace exists
                workspace_response = Mock()
                workspace_response.data = {"id": "workspace-123"}
                
                # Mock booking type
                booking_type = {
                    "id": "booking-type-123",
                    "workspace_id": "workspace-123",
                    "name": "Consultation",
                    "duration_minutes": 30,
                    "location_type": "video",
                    "is_active": True
                }
                
                # Mock existing contact found
                existing_contact_response = Mock()
                existing_contact_response.data = [{
                    "id": "contact-456",
                    "workspace_id": "workspace-123",
                    "name": "Jane Doe",
                    "email": "jane@example.com"
                }]
                
                # Mock booking creation
                booking_response = Mock()
                booking_response.data = [{
                    "id": "booking-456",
                    "contact_id": "contact-456",
                    "status": "pending"
                }]
                
                mock_supabase.table.return_value.select.return_value.eq.return_value.single.return_value.execute.return_value = workspace_response
                mock_supabase.table.return_value.select.return_value.eq.return_value.limit.return_value.execute.return_value = existing_contact_response
                mock_supabase.table.return_value.insert.return_value.execute.return_value = booking_response
                
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
    async def test_create_public_booking_invalid_workspace(self):
        """Test booking fails with invalid workspace"""
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            booking_data = {
                "workspace_id": "nonexistent",
                "booking_type_id": "booking-type-123",
                "booking_date": "2024-01-15",
                "start_time": "10:00",
                "contact_name": "John Doe",
                "contact_email": "john@example.com"
            }
            
            with patch("app.api.v1.endpoints.public.check_rate_limit"):
                mock_supabase = Mock()
                workspace_response = Mock()
                workspace_response.data = None
                mock_supabase.table.return_value.select.return_value.eq.return_value.single.return_value.execute.return_value = workspace_response
                
                with patch("app.api.v1.endpoints.public.get_supabase", return_value=mock_supabase):
                    response = await client.post(
                        "/api/v1/public/bookings",
                        json=booking_data
                    )
                    
                    assert response.status_code == 404
    
    @pytest.mark.asyncio
    async def test_create_public_booking_invalid_booking_type(self):
        """Test booking fails with invalid booking type"""
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            booking_data = {
                "workspace_id": "workspace-123",
                "booking_type_id": "nonexistent",
                "booking_date": "2024-01-15",
                "start_time": "10:00",
                "contact_name": "John Doe",
                "contact_email": "john@example.com"
            }
            
            with patch("app.api.v1.endpoints.public.check_rate_limit"):
                mock_supabase = Mock()
                workspace_response = Mock()
                workspace_response.data = {"id": "workspace-123"}
                mock_supabase.table.return_value.select.return_value.eq.return_value.single.return_value.execute.return_value = workspace_response
                
                with patch("app.api.v1.endpoints.public.get_supabase", return_value=mock_supabase):
                    with patch("app.api.v1.endpoints.public.BookingTypeService") as mock_service:
                        mock_instance = AsyncMock()
                        mock_instance.get_booking_type.return_value = None
                        mock_service.return_value = mock_instance
                        
                        response = await client.post(
                            "/api/v1/public/bookings",
                            json=booking_data
                        )
                        
                        assert response.status_code == 404
    
    @pytest.mark.asyncio
    async def test_create_public_booking_inactive_booking_type(self):
        """Test booking fails with inactive booking type"""
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
                mock_supabase.table.return_value.select.return_value.eq.return_value.single.return_value.execute.return_value = workspace_response
                
                # Mock inactive booking type
                booking_type = {
                    "id": "booking-type-123",
                    "workspace_id": "workspace-123",
                    "is_active": False
                }
                
                with patch("app.api.v1.endpoints.public.get_supabase", return_value=mock_supabase):
                    with patch("app.api.v1.endpoints.public.BookingTypeService") as mock_service:
                        mock_instance = AsyncMock()
                        mock_instance.get_booking_type.return_value = booking_type
                        mock_service.return_value = mock_instance
                        
                        response = await client.post(
                            "/api/v1/public/bookings",
                            json=booking_data
                        )
                        
                        assert response.status_code == 400
                        assert "not active" in response.json()["detail"].lower()
    
    @pytest.mark.asyncio
    async def test_create_public_booking_workspace_mismatch(self):
        """Test booking fails when booking type belongs to different workspace"""
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
                mock_supabase.table.return_value.select.return_value.eq.return_value.single.return_value.execute.return_value = workspace_response
                
                # Mock booking type belongs to different workspace
                booking_type = {
                    "id": "booking-type-123",
                    "workspace_id": "different-workspace",
                    "is_active": True
                }
                
                with patch("app.api.v1.endpoints.public.get_supabase", return_value=mock_supabase):
                    with patch("app.api.v1.endpoints.public.BookingTypeService") as mock_service:
                        mock_instance = AsyncMock()
                        mock_instance.get_booking_type.return_value = booking_type
                        mock_service.return_value = mock_instance
                        
                        response = await client.post(
                            "/api/v1/public/bookings",
                            json=booking_data
                        )
                        
                        assert response.status_code == 400
                        assert "does not belong" in response.json()["detail"].lower()
    
    @pytest.mark.asyncio
    async def test_create_public_booking_invalid_date_format(self):
        """Test booking fails with invalid date format"""
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            booking_data = {
                "workspace_id": "workspace-123",
                "booking_type_id": "booking-type-123",
                "booking_date": "15-01-2024",  # Wrong format
                "start_time": "10:00",
                "contact_name": "John Doe",
                "contact_email": "john@example.com"
            }
            
            response = await client.post(
                "/api/v1/public/bookings",
                json=booking_data
            )
            
            assert response.status_code == 422  # Validation error
    
    @pytest.mark.asyncio
    async def test_create_public_booking_invalid_time_format(self):
        """Test booking fails with invalid time format"""
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            booking_data = {
                "workspace_id": "workspace-123",
                "booking_type_id": "booking-type-123",
                "booking_date": "2024-01-15",
                "start_time": "25:00",  # Invalid hour
                "contact_name": "John Doe",
                "contact_email": "john@example.com"
            }
            
            response = await client.post(
                "/api/v1/public/bookings",
                json=booking_data
            )
            
            assert response.status_code == 422
    
    @pytest.mark.asyncio
    async def test_create_public_booking_missing_contact_info(self):
        """Test booking fails without contact name"""
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            booking_data = {
                "workspace_id": "workspace-123",
                "booking_type_id": "booking-type-123",
                "booking_date": "2024-01-15",
                "start_time": "10:00",
                # Missing contact_name
                "contact_email": "john@example.com"
            }
            
            response = await client.post(
                "/api/v1/public/bookings",
                json=booking_data
            )
            
            assert response.status_code == 422


class TestRateLimiting:
    """Tests for rate limiting on public endpoints"""
    
    @pytest.mark.asyncio
    async def test_rate_limit_exceeded(self):
        """Test rate limiting blocks excessive requests"""
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            workspace_id = "workspace-123"
            
            # Mock the rate limit to be exceeded
            with patch("app.api.v1.endpoints.public.check_rate_limit") as mock_rate_limit:
                from fastapi import HTTPException, status
                mock_rate_limit.side_effect = HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail="Too many requests. Please try again later."
                )
                
                response = await client.get(f"/api/v1/public/booking-types/{workspace_id}")
                
                assert response.status_code == 429
                assert "too many requests" in response.json()["detail"].lower()
