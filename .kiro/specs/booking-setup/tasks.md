
# Step 4: Set Up Bookings - Implementation Tasks

## Task Overview
This document outlines the implementation tasks for the booking setup feature. Tasks are organized by layer (backend, frontend) and should be completed in order.

## Backend Tasks

### 1. Database Schema Verification
- [x] 1.1 Verify booking_types table exists in Supabase
- [x] 1.2 Verify availability table exists in Supabase
- [x] 1.3 Create database indexes for performance
- [x] 1.4 Test database constraints (foreign keys, unique constraints)

### 2. Booking Type Service Implementation
- [x] 2.1 Create BookingTypeService class with CRUD methods
- [x] 2.2 Implement create_booking_type method
- [x] 2.3 Implement get_booking_types method
- [x] 2.4 Implement get_booking_type method
- [x] 2.5 Implement update_booking_type method
- [x] 2.6 Implement delete_booking_type method (soft delete)
- [x] 2.7 Implement set_availability method with overlap validation
- [x] 2.8 Implement get_availability method
- [x] 2.9 Implement get_available_slots method with slot calculation algorithm
- [x] 2.10 Add error handling and logging

### 3. API Endpoints Implementation
- [x] 3.1 Create booking_types.py endpoints file
- [x] 3.2 Implement POST /booking-types endpoint (Owner only - `require_owner`)
- [x] 3.3 Implement GET /booking-types endpoint (Staff or Owner - `require_staff_or_owner`)
- [x] 3.4 Implement GET /booking-types/{id} endpoint (Staff or Owner - `require_staff_or_owner`)
- [x] 3.5 Implement PUT /booking-types/{id} endpoint (Owner only - `require_owner`)
- [x] 3.6 Implement DELETE /booking-types/{id} endpoint (Owner only - `require_owner`)
- [x] 3.7 Implement POST /booking-types/{id}/availability endpoint (Owner only - `require_owner`)
- [x] 3.8 Implement GET /booking-types/{id}/availability endpoint (Staff or Owner - `require_staff_or_owner`)
- [x] 3.9 Implement GET /booking-types/{id}/available-slots endpoint (Staff or Owner - `require_staff_or_owner`)
- [x] 3.10 Add proper role-based authorization using `require_owner` and `require_staff_or_owner`
- [x] 3.11 Add request validation and error handling

### 4. Public Endpoints Implementation
- [x] 4.1 Update public.py with GET /public/booking-types/{workspace_id} endpoint
- [x] 4.2 Update public.py with POST /public/bookings endpoint
- [x] 4.3 Implement public booking creation logic
- [x] 4.4 Create or update contact record on booking
- [x] 4.5 Create conversation for booking
- [x] 4.6 Send confirmation email if integration configured
- [x] 4.7 Send notification to workspace owner
- [x] 4.8 Add rate limiting to public endpoints
- [x] 4.9 Add validation for workspace existence

### 5. Schema Updates
- [x] 5.1 Extend booking.py schemas with BookingTypeCreate
- [x] 5.2 Add BookingTypeUpdate schema
- [x] 5.3 Add BookingTypeResponse schema
- [x] 5.4 Add AvailabilitySlot schema
- [x] 5.5 Add AvailabilityResponse schema
- [x] 5.6 Add PublicBookingCreate schema
- [x] 5.7 Add TimeSlot schema for available slots response
- [x] 5.8 Add validation rules and field constraints

### 6. Router Integration
- [x] 6.1 Import booking_types router in router.py
- [x] 6.2 Include booking_types router with /booking-types prefix
- [x] 6.3 Test all routes are accessible

### 7. Backend Testing
- [x] 7.1 Write unit tests for BookingTypeService
- [x] 7.2 Write unit tests for slot calculation algorithm
- [x] 7.3 Write unit tests for overlap validation
- [x] 7.4 Write integration tests for booking type endpoints
- [x] 7.5 Write integration tests for public booking flow
- [x] 7.6 Test error handling and edge cases
- [x] 7.7 Test timezone handling
- [x] 7.8 Test role-based access control (Owner vs Staff permissions)
- [x] 7.9 Test that Staff users cannot modify booking types or availability
- [x] 7.10 Test that Owner users have full access to all operations

## Frontend Tasks

### 8. API Service Layer
- [x] 8.1 Create bookingType.service.ts file
- [x] 8.2 Implement create booking type API call
- [x] 8.3 Implement list booking types API call
- [x] 8.4 Implement get booking type API call
- [x] 8.5 Implement update booking type API call
- [x] 8.6 Implement delete booking type API call
- [x] 8.7 Implement set availability API call
- [x] 8.8 Implement get availability API call
- [x] 8.9 Implement get available slots API call
- [x] 8.10 Implement get public booking types API call
- [x] 8.11 Implement create public booking API call
- [x] 8.12 Add error handling and type definitions

### 9. Custom Hooks
- [x] 9.1 Create useBookingTypes.ts hook
- [x] 9.2 Implement fetchBookingTypes function
- [x] 9.3 Implement createBookingType function
- [x] 9.4 Implement updateBookingType function
- [x] 9.5 Implement deleteBookingType function
- [x] 9.6 Implement setAvailability function
- [x] 9.7 Implement getAvailability function
- [x] 9.8 Implement getAvailableSlots function
- [x] 9.9 Add loading and error state management
- [x] 9.10 Add optimistic updates for better UX

### 10. Booking Setup Page (Authenticated)
- [x] 10.1 Create BookingSetup.tsx page component
- [x] 10.2 Implement page layout and structure
- [x] 10.3 Create BookingTypeList component
- [x] 10.4 Create BookingTypeForm modal component
- [x] 10.5 Implement booking type creation form (Owner only)
- [x] 10.6 Implement booking type edit functionality (Owner only)
- [x] 10.7 Implement booking type delete functionality (Owner only)
- [x] 10.8 Create AvailabilityScheduler component
- [x] 10.9 Implement weekly calendar UI for availability
- [x] 10.10 Implement add/remove availability slots (Owner only)
- [x] 10.11 Create PublicUrlDisplay component
- [x] 10.12 Implement copy to clipboard functionality
- [x] 10.13 Add validation for completion requirements
- [x] 10.14 Implement skip functionality (Owner only)
- [x] 10.15 Implement continue to Step 5 functionality (Owner only)
- [x] 10.16 Update workspace onboarding_step on completion
- [x] 10.17 Add loading states and error handling
- [x] 10.18 Add responsive design for mobile
- [x] 10.19 Disable edit/delete/availability buttons for Staff users
- [x] 10.20 Show read-only view for Staff users with appropriate messaging

### 11. Public Booking Page
- [x] 11.1 Create PublicBookingPage.tsx component
- [x] 11.2 Implement page layout and branding
- [x] 11.3 Create BookingTypeSelector component
- [x] 11.4 Implement booking type selection UI
- [x] 11.5 Create DatePicker component
- [x] 11.6 Implement calendar with available dates
- [x] 11.7 Create TimeSlotSelector component
- [x] 11.8 Implement time slot selection UI
- [x] 11.9 Create BookingContactForm component
- [x] 11.10 Implement contact information form
- [x] 11.11 Implement form validation
- [x] 11.12 Implement booking submission
- [x] 11.13 Create success confirmation UI
- [x] 11.14 Add error handling and user feedback
- [x] 11.15 Add loading states during API calls
- [x] 11.16 Implement responsive design for mobile
- [x] 11.17 Add accessibility features (ARIA labels, keyboard navigation)

### 12. Type Definitions
- [x] 12.1 Add BookingType interface to types.ts
- [x] 12.2 Add BookingTypeCreate interface
- [x] 12.3 Add BookingTypeUpdate interface
- [x] 12.4 Add AvailabilitySlot interface
- [x] 12.5 Add TimeSlot interface
- [x] 12.6 Add PublicBookingCreate interface
- [x] 12.7 Add PublicBookingResponse interface

### 13. Routing Updates
- [x] 13.1 Add /booking-setup route to App.tsx
- [x] 13.2 Add /public/book/:workspaceId route to App.tsx
- [x] 13.3 Wrap booking-setup with ProtectedRoute
- [x] 13.4 Update ContactFormBuilder to redirect to booking-setup
- [x] 13.5 Test navigation flow from Step 3 to Step 4 to Step 5

### 14. UI/UX Polish
- [x] 14.1 Add icons for booking types (video, phone, in-person)
- [x] 14.2 Add tooltips and help text
- [x] 14.3 Add confirmation dialogs for delete actions
- [x] 14.4 Add success/error toast notifications
- [x] 14.5 Add empty states for no booking types
- [x] 14.6 Add loading skeletons
- [x] 14.7 Ensure consistent styling with existing pages
- [x] 14.8 Test color contrast for accessibility

### 15. Frontend Testing
- [ ] 15.1 Write unit tests for useBookingTypes hook
- [ ] 15.2 Write unit tests for bookingType.service
- [ ] 15.3 Write component tests for BookingSetup page
- [ ] 15.4 Write component tests for PublicBookingPage
- [ ] 15.5 Write integration tests for booking flow
- [ ] 15.6 Test form validation
- [ ] 15.7 Test error handling
- [ ] 15.8 Test responsive design on different screen sizes

## Integration Tasks

### 16. Onboarding Flow Integration
- [ ] 16.1 Update ContactFormBuilder to check completion and redirect
- [ ] 16.2 Update BookingSetup to update workspace.onboarding_step
- [ ] 16.3 Test complete flow from Step 3 to Step 4 to Step 5
- [ ] 16.4 Verify skip functionality works correctly
- [ ] 16.5 Verify back navigation works correctly

### 17. Email Integration
- [ ] 17.1 Create booking confirmation email template
- [ ] 17.2 Create owner notification email template
- [ ] 17.3 Implement email sending in public booking endpoint
- [ ] 17.4 Test email delivery with Resend/SendGrid
- [ ] 17.5 Handle email failures gracefully
- [ ] 17.6 Log email status to alerts table

### 18. Contact Management Integration
- [x] 18.1 Implement contact creation/update in public booking
- [x] 18.2 Implement conversation creation for booking
- [x] 18.3 Link booking to contact and conversation
- [x] 18.4 Test contact deduplication logic
- [x] 18.5 Verify contact data is saved correctly

## Documentation Tasks

### 19. Documentation
- [x] 19.1 Update API_DOCUMENTATION.md with new endpoints
- [x] 19.2 Create STEP4_COMPLETE.md summary document
- [ ] 19.3 Update TESTING_CHECKLIST.md with Step 4 tests
- [x] 19.4 Create user guide for booking setup
- [x] 19.5 Document public booking page URL format
- [x] 19.6 Add troubleshooting guide for common issues

## Deployment Tasks

### 20. Deployment Preparation
- [ ] 20.1 Verify all environment variables are documented
- [ ] 20.2 Run database migrations on staging
- [ ] 20.3 Test complete flow on staging environment
- [ ] 20.4 Verify rate limiting is configured
- [ ] 20.5 Verify error logging is working
- [ ] 20.6 Create deployment checklist
- [ ] 20.7 Deploy to production

## Task Dependencies

**Critical Path**:
1. Database Schema (Task 1) → Backend Service (Task 2)
2. Backend Service (Task 2) → API Endpoints (Task 3, 4)
3. API Endpoints (Task 3, 4) → Schema Updates (Task 5)
4. Schema Updates (Task 5) → Router Integration (Task 6)
5. Router Integration (Task 6) → API Service Layer (Task 8)
6. API Service Layer (Task 8) → Custom Hooks (Task 9)
7. Custom Hooks (Task 9) → Frontend Pages (Task 10, 11)
8. Frontend Pages (Task 10, 11) → Routing Updates (Task 13)
9. All Backend + Frontend → Integration Tasks (Task 16, 17, 18)

**Parallel Work**:
- Type Definitions (Task 12) can be done alongside API Service Layer (Task 8)
- UI/UX Polish (Task 14) can be done after basic pages are complete
- Testing (Task 7, 15) can be done alongside implementation
- Documentation (Task 19) can be done throughout

## Estimated Effort

- Backend Tasks (1-7): 8-10 hours
- Frontend Tasks (8-15): 12-15 hours
- Integration Tasks (16-18): 3-4 hours
- Documentation Tasks (19): 2-3 hours
- Deployment Tasks (20): 2-3 hours

**Total Estimated Effort**: 27-35 hours

## Success Criteria

- [x] Owner can create booking types with all required fields
- [x] Owner can set weekly availability for each booking type
- [x] Owner can view and copy public booking URL
- [x] Public booking page loads without authentication
- [x] Clients can select booking type, date, and time
- [x] Clients can submit booking with contact information
- [x] Booking creates contact and conversation records
- [ ] Confirmation email is sent to client (if configured)
- [ ] Notification email is sent to owner
- [ ] Workspace onboarding_step updates to "bookings_configured"
- [x] Navigation to Step 5 works correctly
- [x] All CRUD operations work smoothly
- [x] Error handling provides clear user feedback
- [x] Responsive design works on mobile devices
- [x] No console errors or warnings
- [x] All tests pass
