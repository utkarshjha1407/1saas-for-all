# Step 4: Set Up Bookings - Design Document

## Architecture Overview

The booking setup feature follows a three-tier architecture:
1. **Backend Services**: Business logic for booking types, availability, and slot calculation
2. **API Layer**: RESTful endpoints for CRUD operations and public booking
3. **Frontend Components**: Setup page for owners and public booking page for clients

## Database Design

### Existing Tables (Already in Schema)
```sql
-- booking_types table
CREATE TABLE booking_types (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    workspace_id UUID NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    duration_minutes INTEGER NOT NULL,
    location_type VARCHAR(50) NOT NULL,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- availability table
CREATE TABLE availability (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    booking_type_id UUID NOT NULL REFERENCES booking_types(id) ON DELETE CASCADE,
    day_of_week INTEGER NOT NULL CHECK (day_of_week >= 0 AND day_of_week <= 6),
    start_time TIME NOT NULL,
    end_time TIME NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    CONSTRAINT no_overlap UNIQUE (booking_type_id, day_of_week, start_time, end_time)
);

-- bookings table (already exists)
-- contacts table (already exists)
-- conversations table (already exists)
```

### Indexes
```sql
CREATE INDEX idx_booking_types_workspace ON booking_types(workspace_id);
CREATE INDEX idx_availability_booking_type ON availability(booking_type_id);
CREATE INDEX idx_bookings_date ON bookings(booking_date);
CREATE INDEX idx_bookings_workspace ON bookings(workspace_id);
```

## Backend Design

### Service Layer: BookingTypeService

**File**: `Backend/app/services/booking_type_service.py`

**Key Methods**:
```python
class BookingTypeService:
    async def create_booking_type(workspace_id, data) -> dict
    async def get_booking_types(workspace_id) -> list[dict]
    async def get_booking_type(booking_type_id) -> dict
    async def update_booking_type(booking_type_id, data) -> dict
    async def delete_booking_type(booking_type_id) -> bool
    async def set_availability(booking_type_id, slots) -> list[dict]
    async def get_availability(booking_type_id) -> list[dict]
    async def get_available_slots(booking_type_id, start_date, end_date) -> list[dict]
    async def validate_no_overlap(booking_type_id, day, start, end) -> bool
```

**Slot Calculation Algorithm**:
```python
def calculate_available_slots(booking_type, date, existing_bookings):
    """
    1. Get availability for the day of week
    2. Generate all possible time slots based on duration
    3. Filter out slots that overlap with existing bookings
    4. Return list of available slots with timestamps
    """
    slots = []
    for availability in day_availability:
        current_time = availability.start_time
        while current_time + duration <= availability.end_time:
            slot_datetime = combine(date, current_time)
            if not overlaps_with_bookings(slot_datetime, duration, existing_bookings):
                slots.append({
                    'start': slot_datetime,
                    'end': slot_datetime + duration,
                    'available': True
                })
            current_time += duration
    return slots
```

### API Layer: Endpoints

**File**: `Backend/app/api/v1/endpoints/booking_types.py`

**Authenticated Endpoints**:

**Owner-Only Endpoints** (configuration/setup - require `require_owner`):
```python
@router.post("/booking-types")
async def create_booking_type(
    data: BookingTypeCreate, 
    current_user: TokenData = Depends(require_owner)
)

@router.put("/booking-types/{booking_type_id}")
async def update_booking_type(
    booking_type_id: str, 
    data: BookingTypeUpdate, 
    current_user: TokenData = Depends(require_owner)
)

@router.delete("/booking-types/{booking_type_id}")
async def delete_booking_type(
    booking_type_id: str, 
    current_user: TokenData = Depends(require_owner)
)

@router.post("/booking-types/{booking_type_id}/availability")
async def set_availability(
    booking_type_id: str, 
    slots: list[AvailabilitySlot], 
    current_user: TokenData = Depends(require_owner)
)
```

**Staff or Owner Endpoints** (viewing/operational - require `require_staff_or_owner`):
```python
@router.get("/booking-types")
async def list_booking_types(
    current_user: TokenData = Depends(require_staff_or_owner)
)

@router.get("/booking-types/{booking_type_id}")
async def get_booking_type(
    booking_type_id: str, 
    current_user: TokenData = Depends(require_staff_or_owner)
)

@router.get("/booking-types/{booking_type_id}/availability")
async def get_availability(
    booking_type_id: str, 
    current_user: TokenData = Depends(require_staff_or_owner)
)

@router.get("/booking-types/{booking_type_id}/available-slots")
async def get_available_slots(
    booking_type_id: str, 
    start_date: str, 
    end_date: str, 
    current_user: TokenData = Depends(require_staff_or_owner)
)
```

**Public Endpoints** (no authentication):
```python
@router.get("/public/booking-types/{workspace_id}")
async def get_public_booking_types(workspace_id: str)

@router.post("/public/bookings")
async def create_public_booking(data: PublicBookingCreate)
```

### Schemas

**File**: `Backend/app/schemas/booking.py` (extend existing)

```python
class BookingTypeCreate(BaseModel):
    name: str = Field(..., min_length=3, max_length=100)
    description: Optional[str] = None
    duration_minutes: int = Field(..., ge=15, le=120)
    location_type: str = Field(..., pattern="^(in-person|phone|video|client-location)$")

class BookingTypeUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=3, max_length=100)
    description: Optional[str] = None
    duration_minutes: Optional[int] = Field(None, ge=15, le=120)
    location_type: Optional[str] = None
    is_active: Optional[bool] = None

class AvailabilitySlot(BaseModel):
    day_of_week: int = Field(..., ge=0, le=6)
    start_time: str = Field(..., pattern="^([0-1][0-9]|2[0-3]):[0-5][0-9]$")
    end_time: str = Field(..., pattern="^([0-1][0-9]|2[0-3]):[0-5][0-9]$")

class PublicBookingCreate(BaseModel):
    workspace_id: str
    booking_type_id: str
    booking_date: str
    start_time: str
    contact_name: str
    contact_email: Optional[str] = None
    contact_phone: Optional[str] = None
    notes: Optional[str] = None
```

## Frontend Design

### Page 1: Booking Setup (Authenticated)

**File**: `frontend/src/pages/BookingSetup.tsx`

**Layout**:
```
┌─────────────────────────────────────────────────┐
│ Step 4: Set Up Bookings                         │
├─────────────────────────────────────────────────┤
│                                                  │
│ Booking Types                    [+ New Type]   │
│ ┌─────────────────────────────────────────────┐ │
│ │ ☑ Initial Consultation (30 min)            │ │
│ │   Video call • Edit • Delete                │ │
│ ├─────────────────────────────────────────────┤ │
│ │ ☑ Follow-up Visit (15 min)                 │ │
│ │   In-person • Edit • Delete                 │ │
│ └─────────────────────────────────────────────┘ │
│                                                  │
│ Availability Schedule                            │
│ ┌─────────────────────────────────────────────┐ │
│ │ Select booking type: [Initial Consultation] │ │
│ │                                              │ │
│ │ Mon  [09:00] - [17:00]  [+ Add Slot]        │ │
│ │ Tue  [09:00] - [17:00]  [+ Add Slot]        │ │
│ │ Wed  [09:00] - [17:00]  [+ Add Slot]        │ │
│ │ Thu  [09:00] - [17:00]  [+ Add Slot]        │ │
│ │ Fri  [09:00] - [17:00]  [+ Add Slot]        │ │
│ │ Sat  Not available                           │ │
│ │ Sun  Not available                           │ │
│ └─────────────────────────────────────────────┘ │
│                                                  │
│ Public Booking URL                               │
│ ┌─────────────────────────────────────────────┐ │
│ │ https://app.com/public/book/workspace-123   │ │
│ │                              [Copy] [Preview]│ │
│ └─────────────────────────────────────────────┘ │
│                                                  │
│                    [Skip] [Continue to Step 5]  │
└─────────────────────────────────────────────────┘
```

**Components**:
- `BookingTypeList`: Display and manage booking types
- `BookingTypeForm`: Create/edit booking type modal
- `AvailabilityScheduler`: Weekly calendar for setting availability
- `PublicUrlDisplay`: Show and copy public booking URL

**State Management**:
```typescript
const [bookingTypes, setBookingTypes] = useState<BookingType[]>([])
const [selectedType, setSelectedType] = useState<string | null>(null)
const [availability, setAvailability] = useState<AvailabilitySlot[]>([])
const [isFormOpen, setIsFormOpen] = useState(false)
```

**Validation**:
- At least one booking type required to continue
- At least one availability slot required to continue
- Show warning if no email integration configured (notifications won't work)

### Page 2: Public Booking Page

**File**: `frontend/src/pages/PublicBookingPage.tsx`

**Layout**:
```
┌─────────────────────────────────────────────────┐
│ [Logo] Workspace Name                           │
│ Book an Appointment                              │
├─────────────────────────────────────────────────┤
│                                                  │
│ Select Service                                   │
│ ┌─────────────────────────────────────────────┐ │
│ │ ○ Initial Consultation                      │ │
│ │   30 minutes • Video call                   │ │
│ │   Description text here...                  │ │
│ ├─────────────────────────────────────────────┤ │
│ │ ○ Follow-up Visit                           │ │
│ │   15 minutes • In-person                    │ │
│ │   Description text here...                  │ │
│ └─────────────────────────────────────────────┘ │
│                                                  │
│ Select Date                                      │
│ ┌─────────────────────────────────────────────┐ │
│ │     February 2026                           │ │
│ │ Su Mo Tu We Th Fr Sa                        │ │
│ │              16 17 18 19                    │ │
│ │ 20 21 22 23 24 25 26                        │ │
│ │ 27 28                                       │ │
│ └─────────────────────────────────────────────┘ │
│                                                  │
│ Available Times (Feb 16)                         │
│ ┌─────────────────────────────────────────────┐ │
│ │ [09:00] [09:30] [10:00] [10:30] [11:00]    │ │
│ │ [13:00] [13:30] [14:00] [14:30] [15:00]    │ │
│ └─────────────────────────────────────────────┘ │
│                                                  │
│ Your Information                                 │
│ ┌─────────────────────────────────────────────┐ │
│ │ Name:  [________________]                   │ │
│ │ Email: [________________]                   │ │
│ │ Phone: [________________]                   │ │
│ │ Notes: [________________]                   │ │
│ │        [________________]                   │ │
│ └─────────────────────────────────────────────┘ │
│                                                  │
│                          [Book Appointment]     │
└─────────────────────────────────────────────────┘
```

**Flow**:
1. Load workspace and booking types
2. User selects booking type
3. Calendar shows available dates (next 60 days)
4. User selects date
5. Load available time slots for that date
6. User selects time slot
7. User fills contact form
8. Submit booking

**Success State**:
```
┌─────────────────────────────────────────────────┐
│ ✓ Booking Confirmed!                            │
│                                                  │
│ Your appointment is scheduled for:               │
│ February 16, 2026 at 10:00 AM                   │
│                                                  │
│ Initial Consultation (30 minutes)                │
│ Video call                                       │
│                                                  │
│ A confirmation email has been sent to:           │
│ client@example.com                               │
│                                                  │
│                          [Done]                  │
└─────────────────────────────────────────────────┘
```

### Hooks and Services

**File**: `frontend/src/hooks/useBookingTypes.ts`
```typescript
export const useBookingTypes = () => {
  const [bookingTypes, setBookingTypes] = useState<BookingType[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const fetchBookingTypes = async () => { ... }
  const createBookingType = async (data: BookingTypeCreate) => { ... }
  const updateBookingType = async (id: string, data: BookingTypeUpdate) => { ... }
  const deleteBookingType = async (id: string) => { ... }
  const setAvailability = async (id: string, slots: AvailabilitySlot[]) => { ... }
  const getAvailability = async (id: string) => { ... }
  const getAvailableSlots = async (id: string, startDate: string, endDate: string) => { ... }

  return {
    bookingTypes,
    loading,
    error,
    fetchBookingTypes,
    createBookingType,
    updateBookingType,
    deleteBookingType,
    setAvailability,
    getAvailability,
    getAvailableSlots
  }
}
```

**File**: `frontend/src/lib/api/services/bookingType.service.ts`
```typescript
export const bookingTypeService = {
  create: (data: BookingTypeCreate) => apiClient.post('/booking-types', data),
  list: () => apiClient.get('/booking-types'),
  get: (id: string) => apiClient.get(`/booking-types/${id}`),
  update: (id: string, data: BookingTypeUpdate) => apiClient.put(`/booking-types/${id}`, data),
  delete: (id: string) => apiClient.delete(`/booking-types/${id}`),
  setAvailability: (id: string, slots: AvailabilitySlot[]) => 
    apiClient.post(`/booking-types/${id}/availability`, { slots }),
  getAvailability: (id: string) => apiClient.get(`/booking-types/${id}/availability`),
  getAvailableSlots: (id: string, startDate: string, endDate: string) =>
    apiClient.get(`/booking-types/${id}/available-slots`, { params: { start_date: startDate, end_date: endDate } }),
  getPublic: (workspaceId: string) => apiClient.get(`/public/booking-types/${workspaceId}`),
  createPublicBooking: (data: PublicBookingCreate) => apiClient.post('/public/bookings', data)
}
```

## Integration Points

### 1. Onboarding Flow
- ContactFormBuilder redirects to `/booking-setup` after completion
- BookingSetup updates workspace.onboarding_step to "bookings_configured"
- BookingSetup redirects to Step 5 (Inventory Setup) after completion

### 2. Email Notifications
- After booking creation, check if email integration exists
- If yes, send confirmation email to client using email_provider
- Send notification email to workspace owner
- Log to alerts table if email fails

### 3. Contact Management
- Create new contact if email/phone doesn't exist
- Update existing contact if found
- Create conversation for the booking
- Link booking to contact and conversation

### 4. Router Updates
**File**: `Backend/app/api/v1/router.py`
```python
from app.api.v1.endpoints import booking_types

api_router.include_router(
    booking_types.router,
    prefix="/booking-types",
    tags=["booking-types"]
)
```

**File**: `frontend/src/App.tsx`
```typescript
<Route path="/booking-setup" element={<ProtectedRoute><BookingSetup /></ProtectedRoute>} />
<Route path="/public/book/:workspaceId" element={<PublicBookingPage />} />
```

## Error Handling

### Backend Errors
- `404 Not Found`: Booking type or workspace doesn't exist
- `400 Bad Request`: Invalid data (duration, time format, overlapping slots)
- `403 Forbidden`: User doesn't own workspace
- `409 Conflict`: Overlapping availability slots
- `422 Unprocessable Entity`: Validation errors

### Frontend Error Messages
- "Please create at least one booking type to continue"
- "Please set availability for at least one booking type"
- "This time slot is no longer available. Please select another."
- "Unable to load available times. Please try again."
- "Booking failed. Please check your information and try again."

## Testing Strategy

### Unit Tests
- BookingTypeService methods
- Slot calculation algorithm
- Availability overlap validation
- Time zone conversion

### Integration Tests
- Create booking type flow
- Set availability flow
- Public booking creation flow
- Email notification sending

### Property-Based Tests
- Slot calculation never produces overlapping slots
- Availability validation catches all overlaps
- Time zone conversions are reversible
- Booking duration always respected

## Performance Considerations

### Optimization Strategies
1. **Caching**: Cache booking types and availability for 5 minutes
2. **Batch Loading**: Load all booking types and availability in single query
3. **Indexed Queries**: Use database indexes for date range queries
4. **Lazy Loading**: Load available slots only when date is selected
5. **Debouncing**: Debounce availability slot calculations on frontend

### Expected Load
- 10-50 booking types per workspace
- 7-14 availability slots per booking type
- 100-500 bookings per month per workspace
- Public page: 100-1000 views per month

## Security Considerations

### Authentication & Authorization
- Booking type CRUD (create, update, delete): Require Owner role (`require_owner`)
- Availability management (set availability): Require Owner role (`require_owner`)
- Viewing operations (list, get, view availability): Allow Staff or Owner (`require_staff_or_owner`)
- Public endpoints: No auth, but validate workspace exists
- Rate limiting: 10 requests/minute per IP on public endpoints

**Role-Based Access Control**:
- **Owner (Admin)**: Can configure booking types, set availability, and view all data
- **Staff**: Can view booking types and availability, but cannot modify configuration

### Data Validation
- Sanitize all user inputs
- Validate time formats strictly
- Prevent SQL injection with parameterized queries
- Validate workspace_id exists before creating bookings

### Privacy
- Public page shows only: workspace name, booking types, availability
- Contact information only collected during booking
- No sensitive workspace data exposed on public page

## Deployment Checklist

- [ ] Database migrations applied (booking_types, availability tables)
- [ ] Backend service implemented and tested
- [ ] API endpoints implemented and tested
- [ ] Frontend pages implemented and tested
- [ ] Router updated with new routes
- [ ] Email templates created for booking confirmations
- [ ] Error handling and logging in place
- [ ] Rate limiting configured
- [ ] Public URL generation working
- [ ] Integration with Step 3 (Contact Form) complete
- [ ] Integration with Step 5 (Inventory) ready

## Future Enhancements (Out of Scope)
- Calendar sync (Google Calendar, Outlook)
- Recurring availability patterns
- Multiple staff scheduling
- Buffer time between bookings
- Booking cancellation/rescheduling UI
- Payment integration
- Automated reminders
- Custom booking fields
- Booking approval workflow
