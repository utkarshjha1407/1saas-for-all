# Step 5: Create Forms - Requirements

## Overview
The form template feature allows workspace owners to create custom forms (intake forms, agreements, questionnaires) that are automatically sent to clients after booking appointments. This is Step 5 in the 8-step onboarding flow.

## User Stories

### US-1: Create Form Templates
As a workspace owner, I want to create custom form templates so that I can collect specific information from clients after they book.

**Acceptance Criteria:**
- 1.1: Owner can create a form template with name and description
- 1.2: Owner can add multiple fields to the form (text, email, phone, textarea, select, checkbox, radio)
- 1.3: Owner can mark fields as required or optional
- 1.4: Owner can reorder fields
- 1.5: Owner can link form to one or more booking types
- 1.6: Owner can preview the form before saving
- 1.7: Form templates are saved to database

### US-2: Link Forms to Booking Types
As a workspace owner, I want to link forms to specific booking types so that the right forms are sent for each service.

**Acceptance Criteria:**
- 2.1: Owner can select which booking types should trigger this form
- 2.2: Multiple forms can be linked to one booking type
- 2.3: One form can be linked to multiple booking types
- 2.4: Owner can view which forms are linked to each booking type

### US-3: Automatic Form Sending
As a workspace owner, I want forms to be sent automatically after bookings so that I don't have to manually follow up.

**Acceptance Criteria:**
- 3.1: When a booking is created, system checks for linked forms
- 3.2: System creates form submission records with status "pending"
- 3.3: System generates unique access token for each submission
- 3.4: System sends email with form link to client (if email integration configured)
- 3.5: Form link is accessible without authentication

### US-4: Client Form Completion
As a client, I want to fill out required forms easily so that I can complete my booking requirements.

**Acceptance Criteria:**
- 4.1: Client receives email with form link
- 4.2: Client can access form via unique URL
- 4.3: Form displays all fields with proper validation
- 4.4: Client can save progress (optional)
- 4.5: Client submits completed form
- 4.6: System updates submission status to "completed"
- 4.7: Client sees confirmation message

### US-5: Form Tracking
As a workspace owner, I want to track form completion status so that I can follow up with clients who haven't completed forms.

**Acceptance Criteria:**
- 5.1: Owner can view all form submissions
- 5.2: Owner can filter by status (pending, in_progress, completed, overdue)
- 5.3: Owner can see which client each submission belongs to
- 5.4: Owner can view submitted form data
- 5.5: System marks forms as overdue after 48 hours
- 5.6: Owner receives alerts for overdue forms

### US-6: Onboarding Flow Integration
As a workspace owner, I want to complete Step 5 and proceed to Step 6 so that I can continue the onboarding process.

**Acceptance Criteria:**
- 6.1: Owner must create at least one form template to complete Step 5
- 6.2: System updates workspace onboarding_step to "forms_configured"
- 6.3: System redirects owner to Step 6 after completion
- 6.4: Owner can skip Step 5 and return later (optional)

## Technical Requirements

### TR-1: Database Schema
- Form templates table with fields: id, workspace_id, name, description, fields (JSONB), booking_type_ids (UUID[])
- Form submissions table with fields: id, form_template_id, booking_id, contact_id, workspace_id, status, data (JSONB), submitted_at

### TR-2: API Endpoints
- POST /api/v1/form-templates - Create form template (Owner only)
- GET /api/v1/form-templates - List form templates (Staff or Owner)
- GET /api/v1/form-templates/{id} - Get form template (Staff or Owner)
- PUT /api/v1/form-templates/{id} - Update form template (Owner only)
- DELETE /api/v1/form-templates/{id} - Delete form template (Owner only)
- GET /api/v1/form-submissions - List submissions (Staff or Owner)
- GET /api/v1/public/forms/{submission_id}/{token} - Get public form (no auth)
- POST /api/v1/public/forms/{submission_id}/{token} - Submit form (no auth)

### TR-3: Frontend Pages
- `/form-builder` - Form template builder (authenticated, Owner only)
- `/public/form/{submission_id}/{token}` - Public form completion page (no auth)

### TR-4: Field Types
Supported field types:
- text: Single-line text input
- email: Email input with validation
- phone: Phone number input
- textarea: Multi-line text input
- select: Dropdown selection
- checkbox: Multiple choice checkboxes
- radio: Single choice radio buttons
- date: Date picker
- number: Numeric input

### TR-5: Validation Rules
- Form name: 3-100 characters, required
- At least one field required
- Field labels: 1-255 characters
- Field types must be valid
- Required flag: boolean
- Options required for select, checkbox, radio fields

### TR-6: Business Logic
- Create form submission when booking is created
- Generate unique access token (UUID)
- Send email with form link if email integration configured
- Mark forms as overdue after 48 hours
- Create alert for overdue forms

## Non-Functional Requirements

### NFR-1: Performance
- Form template creation should complete within 1 second
- Form submission should complete within 2 seconds
- Public form page should load within 2 seconds

### NFR-2: Usability
- Form builder should have drag-and-drop interface (or simple add/remove)
- Field types should have clear icons
- Form preview should match public form appearance
- Error messages should be clear and actionable

### NFR-3: Security
- Public form endpoints must validate submission_id and token
- Authenticated endpoints must verify workspace ownership
- Form data should be sanitized before storage
- Access tokens should be cryptographically secure (UUID v4)

## Dependencies
- Step 1 (Create Workspace) must be completed
- Step 2 (Email/SMS Integration) should be completed for notifications
- Step 4 (Booking Setup) must be completed to link forms
- Supabase database with required tables

## Success Metrics
- Owner can create form template in < 3 minutes
- Owner can link form to booking types in < 1 minute
- Client can complete form in < 5 minutes
- 100% of bookings create form submissions (if forms linked)
- 90% of forms completed within 48 hours

## Out of Scope
- File upload fields
- Conditional logic (show/hide fields based on answers)
- Form versioning
- Form analytics/reporting
- PDF generation from form data
- E-signature fields
- Payment collection
- Multi-page forms
