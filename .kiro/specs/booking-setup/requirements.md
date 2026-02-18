# Step 4: Set Up Bookings - Requirements

## Overview
The booking setup feature allows workspace owners to define service/meeting types, set availability schedules, and generate public booking pages. This is Step 4 in the 8-step onboarding flow for the CareOps hackathon project.

## User Stories

### US-1: Define Booking Types
As a workspace owner, I want to create different types of bookable services/meetings so that clients can choose the appropriate service when booking.

**Acceptance Criteria:**
- 1.1: Owner can create a booking type with name, description, duration, and location
- 1.2: Duration must be in minutes (15, 30, 45, 60, 90, 120)
- 1.3: Location can be "in-person", "phone", "video", or "client-location"
- 1.4: Each booking type has a unique ID and belongs to a workspace
- 1.5: Owner can view a list of all booking types for their workspace
- 1.6: Owner can edit existing booking types
- 1.7: Owner can delete booking types (soft delete with is_active flag)

### US-2: Set Availability Schedule
As a workspace owner, I want to define when I'm available for each booking type so that clients can only book during my available hours.

**Acceptance Criteria:**
- 2.1: Owner can set weekly availability for each booking type
- 2.2: Availability includes day of week, start time, and end time
- 2.3: Multiple time slots can be defined for the same day
- 2.4: Time slots cannot overlap for the same booking type
- 2.5: Availability is stored in workspace timezone
- 2.6: Owner can view current availability schedule
- 2.7: Owner can update or remove availability slots

### US-3: Generate Public Booking Page
As a workspace owner, I want a public booking page URL so that clients can book appointments without authentication.

**Acceptance Criteria:**
- 3.1: System generates a unique public URL for the workspace booking page
- 3.2: Public URL format: `/public/book/{workspace_id}`
- 3.3: Public page displays all active booking types
- 3.4: Public page shows workspace name and contact information
- 3.5: Public page is accessible without authentication
- 3.6: Owner can copy the public URL from the setup page

### US-4: Client Booking Flow
As a client, I want to book an appointment through the public page so that I can schedule a service.

**Acceptance Criteria:**
- 4.1: Client selects a booking type from available options
- 4.2: Client sees available dates based on booking type availability
- 4.3: Client selects a date and sees available time slots
- 4.4: Time slots respect booking duration and existing bookings
- 4.5: Client fills in contact information (name, email/phone)
- 4.6: Client can add optional notes
- 4.7: System creates booking with status "pending"
- 4.8: System creates or updates contact record
- 4.9: System sends confirmation email to client (if email integration configured)
- 4.10: System sends notification to owner

### US-5: Onboarding Flow Integration
As a workspace owner, I want to complete Step 4 and proceed to Step 5 so that I can continue the onboarding process.

**Acceptance Criteria:**
- 5.1: Owner must create at least one booking type to complete Step 4
- 5.2: Owner must set at least one availability slot to complete Step 4
- 5.3: System updates workspace onboarding_step to "bookings_configured"
- 5.4: System redirects owner to Step 5 after completion
- 5.5: Owner can skip Step 4 and return later (optional)

## Technical Requirements

### TR-0: Role-Based Access Control
The system has two internal roles with different permissions:

**Business Owner (Admin) - Role: "owner"**:
- Can create, update, and delete booking types
- Can set and modify availability schedules
- Can view all booking data
- Can configure system settings
- Has full access to all Step 4 features

**Staff User - Role: "staff"**:
- Can view booking types and availability
- Can view booking data
- Cannot create, update, or delete booking types
- Cannot modify availability schedules
- Cannot change system configuration

**Implementation**:
- Use `require_owner` dependency for configuration endpoints (POST, PUT, DELETE, set availability)
- Use `require_staff_or_owner` dependency for viewing endpoints (GET booking types, GET availability)
- Public endpoints have no authentication requirements

### TR-1: Database Schema
- Booking types table with fields: id, workspace_id, name, description, duration_minutes, location_type, is_active, created_at, updated_at
- Availability table with fields: id, booking_type_id, day_of_week, start_time, end_time, created_at, updated_at
- Bookings table already exists with necessary fields

### TR-2: API Endpoints
- POST /api/v1/booking-types - Create booking type
- GET /api/v1/booking-types - List booking types
- GET /api/v1/booking-types/{id} - Get booking type details
- PUT /api/v1/booking-types/{id} - Update booking type
- DELETE /api/v1/booking-types/{id} - Soft delete booking type
- POST /api/v1/booking-types/{id}/availability - Set availability
- GET /api/v1/booking-types/{id}/availability - Get availability
- GET /api/v1/booking-types/{id}/available-slots - Get available time slots for date range
- POST /api/v1/public/bookings - Create booking (public endpoint)
- GET /api/v1/public/booking-types/{workspace_id} - Get public booking types

### TR-3: Frontend Pages
- `/booking-setup` - Booking type management and availability scheduler (authenticated)
- `/public/book/:workspaceId` - Public booking page (no auth)

### TR-4: Validation Rules
- Booking type name: 3-100 characters, required
- Duration: Must be one of [15, 30, 45, 60, 90, 120] minutes
- Location type: Must be one of ["in-person", "phone", "video", "client-location"]
- Availability times: Must be valid time format (HH:MM)
- Day of week: Must be 0-6 (Sunday-Saturday)
- No overlapping availability slots for same booking type

### TR-5: Business Logic
- Calculate available time slots based on:
  - Booking type availability schedule
  - Existing bookings (avoid double-booking)
  - Booking duration
  - Workspace timezone
- Buffer time between bookings: 0 minutes (back-to-back allowed)
- Booking window: 60 days in advance (configurable)

## Non-Functional Requirements

### NFR-1: Performance
- Available slots calculation should complete within 500ms
- Public booking page should load within 2 seconds

### NFR-2: Usability
- Availability scheduler should use visual calendar interface
- Time slot selection should be intuitive and mobile-friendly
- Error messages should be clear and actionable

### NFR-3: Security
- Public endpoints must validate workspace_id exists
- Authenticated endpoints must verify workspace ownership
- Rate limiting on public booking endpoint (10 requests/minute per IP)

## Dependencies
- Step 1 (Create Workspace) must be completed
- Step 2 (Email/SMS Integration) should be completed for notifications
- Supabase database with required tables
- Frontend routing and authentication

## Success Metrics
- Owner can create booking type in < 2 minutes
- Owner can set weekly availability in < 3 minutes
- Client can complete booking in < 2 minutes
- 100% of bookings create contact records
- 95% of bookings send confirmation emails (when configured)

## Out of Scope
- Recurring availability patterns (e.g., "every other week")
- Multiple staff member scheduling
- Payment integration
- Calendar sync (Google Calendar, Outlook)
- Booking cancellation/rescheduling (handled in later steps)
- Automated reminders (handled in later steps)
