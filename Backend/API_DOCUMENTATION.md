# CareOps API Documentation

Base URL: `http://localhost:8000/api/v1`

## Authentication

All authenticated endpoints require a Bearer token in the Authorization header:

```
Authorization: Bearer <your_jwt_token>
```

### Get Token

**Register**
```http
POST /auth/register
Content-Type: application/json

{
  "email": "owner@example.com",
  "password": "SecurePass123!",
  "full_name": "John Doe"
}

Response: 201 Created
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "token_type": "bearer"
}
```

**Login**
```http
POST /auth/login
Content-Type: application/json

{
  "email": "owner@example.com",
  "password": "SecurePass123!"
}

Response: 200 OK
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "token_type": "bearer"
}
```

## Workspace Management

### Create Workspace

```http
POST /workspaces
Authorization: Bearer <token>
Content-Type: application/json

{
  "name": "Acme Services",
  "address": "123 Main St, City, State 12345",
  "timezone": "America/New_York",
  "contact_email": "contact@acme.com"
}

Response: 201 Created
{
  "id": "uuid",
  "name": "Acme Services",
  "address": "123 Main St, City, State 12345",
  "timezone": "America/New_York",
  "contact_email": "contact@acme.com",
  "status": "setup",
  "onboarding_step": "workspace_created",
  "owner_id": "uuid",
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z"
}
```

### Get Onboarding Status

```http
GET /workspaces/{workspace_id}/onboarding
Authorization: Bearer <token>

Response: 200 OK
{
  "current_step": "workspace_created",
  "completed_steps": ["workspace_created"],
  "is_complete": false,
  "next_step": "communication_setup",
  "missing_requirements": [
    "At least one communication channel",
    "At least one booking type",
    "Availability schedule"
  ]
}
```

### Activate Workspace

```http
POST /workspaces/{workspace_id}/activate
Authorization: Bearer <token>

Response: 200 OK
{
  "id": "uuid",
  "status": "active",
  "onboarding_step": "activated",
  ...
}
```

## Booking Management

### Create Booking (Public)

```http
POST /bookings?workspace_id={workspace_id}
Content-Type: application/json

{
  "booking_type_id": "uuid",
  "contact_name": "Jane Smith",
  "contact_email": "jane@example.com",
  "contact_phone": "+1234567890",
  "scheduled_at": "2024-01-15T14:00:00Z",
  "notes": "First time customer"
}

Response: 200 OK
{
  "id": "uuid",
  "workspace_id": "uuid",
  "booking_type_id": "uuid",
  "contact_id": "uuid",
  "scheduled_at": "2024-01-15T14:00:00Z",
  "status": "pending",
  "notes": "First time customer",
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z"
}
```

### Get Today's Bookings

```http
GET /bookings/today
Authorization: Bearer <token>

Response: 200 OK
[
  {
    "id": "uuid",
    "workspace_id": "uuid",
    "booking_type_id": "uuid",
    "contact_id": "uuid",
    "scheduled_at": "2024-01-01T14:00:00Z",
    "status": "confirmed",
    "notes": null,
    "created_at": "2024-01-01T00:00:00Z",
    "updated_at": "2024-01-01T00:00:00Z"
  }
]
```

### Update Booking Status

```http
POST /bookings/{booking_id}/status?status=completed
Authorization: Bearer <token>

Response: 200 OK
{
  "id": "uuid",
  "status": "completed",
  ...
}
```

## Contact Management

### Create Contact (Public)

```http
POST /contacts?workspace_id={workspace_id}
Content-Type: application/json

{
  "name": "John Customer",
  "email": "john@example.com",
  "phone": "+1234567890",
  "message": "I'm interested in your services"
}

Response: 200 OK
{
  "id": "uuid",
  "workspace_id": "uuid",
  "name": "John Customer",
  "email": "john@example.com",
  "phone": "+1234567890",
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z"
}
```

### Get All Contacts

```http
GET /contacts
Authorization: Bearer <token>

Response: 200 OK
[
  {
    "id": "uuid",
    "workspace_id": "uuid",
    "name": "John Customer",
    "email": "john@example.com",
    "phone": "+1234567890",
    "created_at": "2024-01-01T00:00:00Z",
    "updated_at": "2024-01-01T00:00:00Z"
  }
]
```

## Messaging (Inbox)

### Get Conversations

```http
GET /messages/conversations
Authorization: Bearer <token>

Response: 200 OK
[
  {
    "id": "uuid",
    "workspace_id": "uuid",
    "contact_id": "uuid",
    "last_message_at": "2024-01-01T12:00:00Z",
    "unread_count": 2,
    "is_automated_paused": false,
    "created_at": "2024-01-01T00:00:00Z"
  }
]
```

### Get Messages in Conversation

```http
GET /messages/conversations/{conversation_id}/messages
Authorization: Bearer <token>

Response: 200 OK
[
  {
    "id": "uuid",
    "conversation_id": "uuid",
    "sender_id": null,
    "content": "Welcome! Thanks for contacting us.",
    "channel": "email",
    "message_type": "automated",
    "is_read": true,
    "sent_at": "2024-01-01T10:00:00Z"
  },
  {
    "id": "uuid",
    "conversation_id": "uuid",
    "sender_id": "uuid",
    "content": "Hi! How can I help you?",
    "channel": "email",
    "message_type": "manual",
    "is_read": false,
    "sent_at": "2024-01-01T11:00:00Z"
  }
]
```

### Send Message

```http
POST /messages/conversations/{conversation_id}/messages
Authorization: Bearer <token>
Content-Type: application/json

{
  "conversation_id": "uuid",
  "content": "Thanks for reaching out! I'll help you with that.",
  "channel": "email",
  "is_automated": false
}

Response: 200 OK
{
  "id": "uuid",
  "conversation_id": "uuid",
  "sender_id": "uuid",
  "content": "Thanks for reaching out! I'll help you with that.",
  "channel": "email",
  "message_type": "manual",
  "is_read": false,
  "sent_at": "2024-01-01T12:00:00Z"
}
```

## Forms

### Create Form Template

```http
POST /forms/templates
Authorization: Bearer <token>
Content-Type: application/json

{
  "name": "Client Intake Form",
  "description": "Initial client information",
  "fields": [
    {
      "name": "full_name",
      "type": "text",
      "label": "Full Name",
      "required": true
    },
    {
      "name": "date_of_birth",
      "type": "date",
      "label": "Date of Birth",
      "required": true
    }
  ],
  "booking_type_ids": ["uuid1", "uuid2"]
}

Response: 200 OK
{
  "id": "uuid",
  "workspace_id": "uuid",
  "name": "Client Intake Form",
  "description": "Initial client information",
  "fields": [...],
  "booking_type_ids": ["uuid1", "uuid2"],
  "created_at": "2024-01-01T00:00:00Z"
}
```

### Submit Form (Public)

```http
POST /forms/submissions
Content-Type: application/json

{
  "form_template_id": "uuid",
  "booking_id": "uuid",
  "data": {
    "full_name": "John Doe",
    "date_of_birth": "1990-01-01"
  }
}

Response: 200 OK
{
  "id": "uuid",
  "form_template_id": "uuid",
  "booking_id": "uuid",
  "contact_id": "uuid",
  "status": "pending",
  "data": {...},
  "submitted_at": null,
  "created_at": "2024-01-01T00:00:00Z"
}
```

### Get Form Submissions

```http
GET /forms/submissions?status=pending
Authorization: Bearer <token>

Response: 200 OK
[
  {
    "id": "uuid",
    "form_template_id": "uuid",
    "booking_id": "uuid",
    "contact_id": "uuid",
    "status": "pending",
    "data": {...},
    "submitted_at": null,
    "created_at": "2024-01-01T00:00:00Z"
  }
]
```

## Inventory

### Create Inventory Item

```http
POST /inventory
Authorization: Bearer <token>
Content-Type: application/json

{
  "name": "Massage Oil",
  "description": "Lavender scented",
  "quantity": 50,
  "low_stock_threshold": 10,
  "unit": "bottles"
}

Response: 200 OK
{
  "id": "uuid",
  "workspace_id": "uuid",
  "name": "Massage Oil",
  "description": "Lavender scented",
  "quantity": 50,
  "low_stock_threshold": 10,
  "unit": "bottles",
  "is_low_stock": false,
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z"
}
```

### Get Low Stock Items

```http
GET /inventory/low-stock
Authorization: Bearer <token>

Response: 200 OK
[
  {
    "id": "uuid",
    "workspace_id": "uuid",
    "name": "Massage Oil",
    "quantity": 8,
    "low_stock_threshold": 10,
    "is_low_stock": true,
    ...
  }
]
```

### Record Inventory Usage

```http
POST /inventory/usage
Authorization: Bearer <token>
Content-Type: application/json

{
  "inventory_item_id": "uuid",
  "booking_id": "uuid",
  "quantity_used": 2,
  "notes": "Used for massage session"
}

Response: 200 OK
{
  "id": "uuid",
  "inventory_item_id": "uuid",
  "booking_id": "uuid",
  "quantity_used": 2,
  "notes": "Used for massage session",
  "created_at": "2024-01-01T00:00:00Z"
}
```

## Dashboard

### Get Dashboard Statistics

```http
GET /dashboard/stats
Authorization: Bearer <token>

Response: 200 OK
{
  "bookings": {
    "today_count": 5,
    "upcoming_count": 12,
    "completed_count": 3,
    "no_show_count": 1
  },
  "leads": {
    "new_inquiries": 8,
    "ongoing_conversations": 15,
    "unanswered_messages": 3
  },
  "forms": {
    "pending_count": 4,
    "overdue_count": 1,
    "completed_count": 20
  },
  "inventory": {
    "low_stock_items": 2,
    "critical_items": 0
  },
  "total_alerts": 5,
  "critical_alerts": 1,
  "generated_at": "2024-01-01T12:00:00Z"
}
```

## Integrations

### Create Integration

```http
POST /integrations
Authorization: Bearer <token>
Content-Type: application/json

{
  "provider": "resend",
  "config": {
    "api_key": "re_xxxxx",
    "from_email": "noreply@acme.com"
  }
}

Response: 200 OK
{
  "id": "uuid",
  "workspace_id": "uuid",
  "provider": "resend",
  "config": {...},
  "status": "active",
  "created_at": "2024-01-01T00:00:00Z"
}
```

## Error Responses

All errors follow this format:

```json
{
  "detail": "Human-readable error message",
  "error_code": "MACHINE_READABLE_CODE"
}
```

### Common Error Codes

- `NOT_FOUND` (404): Resource not found
- `UNAUTHORIZED` (401): Invalid or missing authentication
- `FORBIDDEN` (403): Insufficient permissions
- `VALIDATION_ERROR` (422): Invalid input data
- `CONFLICT` (409): Resource conflict (e.g., duplicate)
- `INTEGRATION_ERROR` (503): External service failure
- `INTERNAL_ERROR` (500): Unexpected server error

## Rate Limiting

- Default: 60 requests per minute per IP
- Authenticated: 120 requests per minute per user
- Headers:
  - `X-RateLimit-Limit`: Maximum requests
  - `X-RateLimit-Remaining`: Remaining requests
  - `X-RateLimit-Reset`: Reset timestamp

## Webhooks (Coming Soon)

Subscribe to events:
- `booking.created`
- `booking.updated`
- `form.submitted`
- `inventory.low_stock`
- `message.received`

## Testing

Use the interactive API documentation:
- Swagger UI: http://localhost:8000/api/v1/docs
- ReDoc: http://localhost:8000/api/v1/redoc

## Postman Collection

Import the API into Postman:
1. Create new collection
2. Import OpenAPI spec: http://localhost:8000/api/v1/openapi.json
3. Set environment variable `base_url` = `http://localhost:8000/api/v1`
4. Set environment variable `token` = `<your_jwt_token>`

## Support

For API issues or questions:
- Check logs: `docker-compose logs api`
- Review documentation: `/api/v1/docs`
- Contact: dev@careops.com
