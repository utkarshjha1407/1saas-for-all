# Role-Based Access Control - Step 4 Alignment

## System Roles Overview

The CareOps system has **two internal roles** with distinct permissions:

### 1. Business Owner (Admin) - Role: `owner`
**Focus**: Visibility, control, and configuration

**Permissions**:
- ✅ Sets up the business
- ✅ Configures the system
- ✅ Monitors performance
- ✅ Intervenes when required
- ✅ Full access to all features

### 2. Staff User - Role: `staff`
**Focus**: Daily operations and customer interaction

**Permissions**:
- ✅ Handle customer communication
- ✅ Manage bookings
- ✅ Track form completion
- ✅ Update booking status
- ❌ Cannot change system configuration
- ❌ Cannot modify automation rules
- ❌ Cannot manage integrations

## Step 4: Booking Setup - RBAC Implementation

### Backend Endpoints Authorization

#### Owner-Only Endpoints (Configuration)
These endpoints modify system configuration and require `require_owner` dependency:

| Endpoint | Method | Purpose | Authorization |
|----------|--------|---------|---------------|
| `/booking-types` | POST | Create booking type | `require_owner` |
| `/booking-types/{id}` | PUT | Update booking type | `require_owner` |
| `/booking-types/{id}` | DELETE | Delete booking type | `require_owner` |
| `/booking-types/{id}/availability` | POST | Set availability schedule | `require_owner` |

**Rationale**: Creating, modifying, and deleting booking types is system configuration that only the business owner should control.

#### Staff or Owner Endpoints (Viewing/Operations)
These endpoints allow viewing data and require `require_staff_or_owner` dependency:

| Endpoint | Method | Purpose | Authorization |
|----------|--------|---------|---------------|
| `/booking-types` | GET | List all booking types | `require_staff_or_owner` |
| `/booking-types/{id}` | GET | Get booking type details | `require_staff_or_owner` |
| `/booking-types/{id}/availability` | GET | View availability schedule | `require_staff_or_owner` |
| `/booking-types/{id}/available-slots` | GET | Get available time slots | `require_staff_or_owner` |

**Rationale**: Staff need to view booking types and availability to help customers and manage bookings, but don't need to modify the configuration.

#### Public Endpoints (No Authentication)
These endpoints are accessible to clients without authentication:

| Endpoint | Method | Purpose | Authorization |
|----------|--------|---------|---------------|
| `/public/booking-types/{workspace_id}` | GET | Get public booking types | None (public) |
| `/public/bookings` | POST | Create booking | None (public) |

**Rationale**: Clients need to view available services and book appointments without creating an account.

### Frontend UI Authorization

#### BookingSetup Page (`/booking-setup`)

**Owner View**:
```
┌─────────────────────────────────────────────────┐
│ Step 4: Set Up Bookings                         │
├─────────────────────────────────────────────────┤
│ Booking Types                    [+ New Type]   │ ← Owner can add
│ ┌─────────────────────────────────────────────┐ │
│ │ ☑ Initial Consultation (30 min)            │ │
│ │   Video call • [Edit] • [Delete]           │ │ ← Owner can edit/delete
│ └─────────────────────────────────────────────┘ │
│                                                  │
│ Availability Schedule                            │
│ ┌─────────────────────────────────────────────┐ │
│ │ Mon  [09:00] - [17:00]  [+ Add Slot] [×]   │ │ ← Owner can modify
│ └─────────────────────────────────────────────┘ │
│                                                  │
│                    [Skip] [Continue to Step 5]  │ ← Owner controls flow
└─────────────────────────────────────────────────┘
```

**Staff View** (Read-Only):
```
┌─────────────────────────────────────────────────┐
│ Booking Types (View Only)                       │
├─────────────────────────────────────────────────┤
│ ℹ️ Only workspace owners can modify booking     │
│   types and availability schedules.             │
├─────────────────────────────────────────────────┤
│ Booking Types                                    │ ← No "Add" button
│ ┌─────────────────────────────────────────────┐ │
│ │ ☑ Initial Consultation (30 min)            │ │
│ │   Video call                                │ │ ← No Edit/Delete buttons
│ └─────────────────────────────────────────────┘ │
│                                                  │
│ Availability Schedule                            │
│ ┌─────────────────────────────────────────────┐ │
│ │ Mon  09:00 - 17:00                          │ │ ← Read-only display
│ └─────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────┘
```

**UI Implementation**:
```typescript
// Check user role from auth context
const { user } = useAuth()
const isOwner = user?.role === 'owner'

// Conditionally render buttons
{isOwner && (
  <Button onClick={handleCreateBookingType}>
    + New Type
  </Button>
)}

// Disable edit/delete for staff
<Button 
  onClick={handleEdit} 
  disabled={!isOwner}
>
  Edit
</Button>

// Show informational message for staff
{!isOwner && (
  <Alert>
    <Info className="h-4 w-4" />
    <AlertDescription>
      Only workspace owners can modify booking types and availability.
    </AlertDescription>
  </Alert>
)}
```

### Consistency with Other Steps

#### Step 2: Email & SMS Integration
- **Current**: Uses `require_owner` for all integration endpoints ✅
- **Rationale**: Integrations are system configuration (Owner only)

#### Step 3: Contact Form Builder
- **Current**: Uses `require_owner` for form configuration ✅
- **Rationale**: Contact form setup is system configuration (Owner only)

#### Step 4: Booking Setup (This Step)
- **Configuration**: Uses `require_owner` for booking type CRUD and availability ✅
- **Viewing**: Uses `require_staff_or_owner` for viewing booking types ✅
- **Rationale**: Consistent with system design - configuration is Owner-only, viewing is Staff-accessible

#### Operational Endpoints (Existing)
- **Bookings Management**: Uses `require_staff_or_owner` ✅
- **Contacts Management**: Uses `require_staff_or_owner` ✅
- **Messages**: Uses `require_staff_or_owner` ✅
- **Dashboard**: Uses `require_staff_or_owner` ✅
- **Rationale**: Staff handle daily operations

## Authorization Flow

### Backend Authorization Check
```python
from app.core.security import require_owner, require_staff_or_owner
from app.schemas.auth import TokenData

# Owner-only endpoint
@router.post("/booking-types")
async def create_booking_type(
    data: BookingTypeCreate,
    current_user: TokenData = Depends(require_owner)  # ← Enforces owner role
):
    # Only executes if user.role == 'owner'
    # Returns 403 Forbidden if user.role == 'staff'
    ...

# Staff or Owner endpoint
@router.get("/booking-types")
async def list_booking_types(
    current_user: TokenData = Depends(require_staff_or_owner)  # ← Allows both roles
):
    # Executes if user.role in ['owner', 'staff']
    # Returns 403 Forbidden for any other role
    ...
```

### Frontend Authorization Check
```typescript
// Get user from auth context
const { user } = useAuth()

// Check role before API call
const handleCreateBookingType = async (data: BookingTypeCreate) => {
  if (user?.role !== 'owner') {
    toast.error('Only workspace owners can create booking types')
    return
  }
  
  try {
    await bookingTypeService.create(data)
    toast.success('Booking type created')
  } catch (error) {
    if (error.status === 403) {
      toast.error('You do not have permission to perform this action')
    }
  }
}
```

## Error Handling

### 403 Forbidden Responses
When a Staff user attempts to access an Owner-only endpoint:

**Backend Response**:
```json
{
  "detail": "Owner access required"
}
```

**Frontend Handling**:
```typescript
try {
  await bookingTypeService.create(data)
} catch (error) {
  if (error.status === 403) {
    toast.error('Only workspace owners can modify booking types')
  }
}
```

## Testing Strategy

### Backend Tests
```python
def test_staff_cannot_create_booking_type():
    """Staff users should receive 403 when trying to create booking types"""
    # Login as staff user
    staff_token = login_as_staff()
    
    # Attempt to create booking type
    response = client.post(
        "/api/v1/booking-types",
        headers={"Authorization": f"Bearer {staff_token}"},
        json={"name": "Test", "duration_minutes": 30, "location_type": "video"}
    )
    
    assert response.status_code == 403
    assert response.json()["detail"] == "Owner access required"

def test_staff_can_view_booking_types():
    """Staff users should be able to view booking types"""
    # Login as staff user
    staff_token = login_as_staff()
    
    # View booking types
    response = client.get(
        "/api/v1/booking-types",
        headers={"Authorization": f"Bearer {staff_token}"}
    )
    
    assert response.status_code == 200
    assert isinstance(response.json(), list)
```

### Frontend Tests
```typescript
describe('BookingSetup - Role-Based Access', () => {
  it('should hide create button for staff users', () => {
    // Mock staff user
    mockUseAuth({ user: { role: 'staff' } })
    
    render(<BookingSetup />)
    
    expect(screen.queryByText('+ New Type')).not.toBeInTheDocument()
  })
  
  it('should show create button for owner users', () => {
    // Mock owner user
    mockUseAuth({ user: { role: 'owner' } })
    
    render(<BookingSetup />)
    
    expect(screen.getByText('+ New Type')).toBeInTheDocument()
  })
  
  it('should disable edit buttons for staff users', () => {
    mockUseAuth({ user: { role: 'staff' } })
    
    render(<BookingSetup />)
    
    const editButtons = screen.getAllByText('Edit')
    editButtons.forEach(button => {
      expect(button).toBeDisabled()
    })
  })
})
```

## Summary

✅ **Step 4 is fully aligned with the two-role system**:
- Owner (Admin) has full control over booking type configuration
- Staff can view booking types and availability for operational purposes
- Staff cannot modify system configuration
- Public endpoints allow clients to book without authentication
- Consistent with existing role implementation in Steps 1-3
- Proper error handling for unauthorized access
- Clear UI feedback for role-based restrictions

This implementation ensures that the business owner maintains control over the booking system configuration while allowing staff to access the information they need for daily operations.
