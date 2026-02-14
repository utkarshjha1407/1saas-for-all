# CareOps Backend - System Overview

Visual guide to understanding the CareOps backend architecture.

## 🏗️ High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                         FRONTEND                            │
│                    (React/Next.js)                          │
└─────────────────────────────────────────────────────────────┘
                            │
                            │ HTTPS/REST API
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                      FASTAPI BACKEND                        │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │     Auth     │  │   Business   │  │  Background  │     │
│  │  Middleware  │  │    Logic     │  │    Tasks     │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
└─────────────────────────────────────────────────────────────┘
         │                    │                    │
         │                    │                    │
         ▼                    ▼                    ▼
┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│   Supabase   │    │  Email/SMS   │    │    Redis     │
│  (Postgres)  │    │  Providers   │    │   (Queue)    │
└──────────────┘    └──────────────┘    └──────────────┘
```

## 🔄 Request Flow

### 1. Customer Booking Flow

```
Customer
   │
   │ 1. Opens booking page
   ▼
Public API (No Auth)
   │
   │ 2. POST /bookings
   ▼
Booking Service
   │
   ├─→ 3. Validate booking type
   ├─→ 4. Check availability
   ├─→ 5. Create contact (if new)
   └─→ 6. Create booking
   │
   ▼
Database (Supabase)
   │
   │ 7. Trigger events
   ▼
Celery Tasks
   │
   ├─→ Send confirmation email
   ├─→ Send forms
   ├─→ Create conversation
   └─→ Schedule reminder
```

### 2. Staff Daily Flow

```
Staff User
   │
   │ 1. Login
   ▼
Auth Endpoint
   │
   │ 2. Validate credentials
   │ 3. Generate JWT
   ▼
Staff Dashboard
   │
   ├─→ View today's bookings
   ├─→ Check inbox
   ├─→ Review forms
   └─→ Monitor inventory
   │
   │ 4. Reply to message
   ▼
Message Endpoint
   │
   │ 5. Pause automation
   │ 6. Send message
   ▼
Email/SMS Provider
```

### 3. Owner Onboarding Flow

```
Owner
   │
   │ 1. Register
   ▼
Create Account
   │
   │ 2. Create workspace
   ▼
Workspace Service
   │
   ├─→ 3. Setup communication
   ├─→ 4. Create booking types
   ├─→ 5. Define availability
   ├─→ 6. Upload forms
   ├─→ 7. Add inventory
   ├─→ 8. Invite staff
   │
   │ 9. Validate requirements
   ▼
Activate Workspace
```

## 📊 Data Model

### Core Entities

```
┌──────────────┐
│    Users     │
│──────────────│
│ id           │
│ email        │
│ role         │◄────┐
│ workspace_id │     │
└──────────────┘     │
                     │
┌──────────────┐     │
│  Workspaces  │     │
│──────────────│     │
│ id           │─────┘
│ name         │
│ status       │
│ owner_id     │
└──────────────┘
       │
       │ has many
       ▼
┌──────────────┐     ┌──────────────┐
│   Contacts   │────▶│  Bookings    │
│──────────────│     │──────────────│
│ id           │     │ id           │
│ name         │     │ contact_id   │
│ email        │     │ scheduled_at │
│ phone        │     │ status       │
└──────────────┘     └──────────────┘
       │                    │
       │                    │
       ▼                    ▼
┌──────────────┐     ┌──────────────┐
│Conversations │     │    Forms     │
│──────────────│     │──────────────│
│ id           │     │ id           │
│ contact_id   │     │ booking_id   │
│ unread_count │     │ status       │
└──────────────┘     └──────────────┘
       │
       │ has many
       ▼
┌──────────────┐
│   Messages   │
│──────────────│
│ id           │
│ content      │
│ channel      │
│ message_type │
└──────────────┘
```

### Relationships

- **User** belongs to **Workspace**
- **Workspace** has many **Contacts**, **Bookings**, **Forms**, **Inventory**
- **Contact** has many **Bookings**, **Conversations**
- **Booking** has many **Form Submissions**, **Inventory Usage**
- **Conversation** has many **Messages**

## 🎯 Service Layer Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    API ENDPOINTS                        │
│  (Handle HTTP, Validation, Response Formatting)        │
└─────────────────────────────────────────────────────────┘
                         │
                         │ Calls
                         ▼
┌─────────────────────────────────────────────────────────┐
│                   SERVICE LAYER                         │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐ │
│  │  Workspace   │  │   Booking    │  │   Contact    │ │
│  │   Service    │  │   Service    │  │   Service    │ │
│  └──────────────┘  └──────────────┘  └──────────────┘ │
│  (Business Logic, Validation, Orchestration)           │
└─────────────────────────────────────────────────────────┘
                         │
                         │ Uses
                         ▼
┌─────────────────────────────────────────────────────────┐
│                  REPOSITORY LAYER                       │
│  ┌──────────────────────────────────────────────────┐  │
│  │           Base Service (CRUD)                    │  │
│  │  - get_by_id()                                   │  │
│  │  - get_all()                                     │  │
│  │  - create()                                      │  │
│  │  - update()                                      │  │
│  │  - delete()                                      │  │
│  └──────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
                         │
                         │ Queries
                         ▼
┌─────────────────────────────────────────────────────────┐
│                  SUPABASE (PostgreSQL)                  │
└─────────────────────────────────────────────────────────┘
```

## 🔐 Authentication Flow

```
1. User Login
   │
   ▼
┌─────────────────┐
│ POST /auth/login│
│ {email, pass}   │
└─────────────────┘
   │
   ▼
┌─────────────────┐
│ Verify Password │
│ (bcrypt)        │
└─────────────────┘
   │
   ▼
┌─────────────────┐
│ Generate JWT    │
│ {user_id, role} │
└─────────────────┘
   │
   ▼
┌─────────────────┐
│ Return Token    │
└─────────────────┘

2. Authenticated Request
   │
   ▼
┌─────────────────┐
│ Authorization:  │
│ Bearer <token>  │
└─────────────────┘
   │
   ▼
┌─────────────────┐
│ Decode JWT      │
│ Verify Signature│
└─────────────────┘
   │
   ▼
┌─────────────────┐
│ Check Role      │
│ (Owner/Staff)   │
└─────────────────┘
   │
   ▼
┌─────────────────┐
│ Process Request │
└─────────────────┘
```

## 🤖 Automation System

### Event-Driven Architecture

```
┌─────────────────┐
│  User Action    │
└─────────────────┘
        │
        ▼
┌─────────────────┐
│  API Endpoint   │
└─────────────────┘
        │
        ▼
┌─────────────────┐
│  Service Layer  │
└─────────────────┘
        │
        ├─→ Database Update
        │
        └─→ Trigger Event
                │
                ▼
        ┌─────────────────┐
        │  Celery Task    │
        │  (Background)   │
        └─────────────────┘
                │
                ├─→ Send Email
                ├─→ Send SMS
                ├─→ Create Alert
                └─→ Update Status
```

### Automation Rules

```
Event: Contact Created
   │
   └─→ Task: send_welcome_message
       │
       ├─→ Get contact details
       ├─→ Get workspace info
       ├─→ Send email via provider
       └─→ Log result

Event: Booking Created
   │
   ├─→ Task: send_booking_confirmation
   │   │
   │   ├─→ Get booking details
   │   ├─→ Format confirmation
   │   └─→ Send email
   │
   └─→ Task: send_form_after_booking
       │
       ├─→ Get form templates
       ├─→ Create submissions
       └─→ Send forms

Scheduled: Every 30 minutes
   │
   └─→ Task: send_booking_reminders
       │
       ├─→ Find bookings in next 24h
       ├─→ For each booking:
       │   ├─→ Send email reminder
       │   └─→ Send SMS reminder
       └─→ Log results

Scheduled: Every hour
   │
   ├─→ Task: check_overdue_forms
   │   │
   │   ├─→ Find forms > 48h old
   │   ├─→ Update status to overdue
   │   └─→ Create alerts
   │
   └─→ Task: check_inventory_levels
       │
       ├─→ Find low stock items
       ├─→ Create alerts
       └─→ Notify owner
```

## 📧 Communication System

### Multi-Provider Architecture

```
┌─────────────────┐
│  Send Message   │
└─────────────────┘
        │
        ▼
┌─────────────────┐
│ Email Service   │
└─────────────────┘
        │
        ├─→ Try Provider 1 (Resend)
        │   │
        │   ├─→ Success → Return
        │   └─→ Failure → Continue
        │
        └─→ Try Provider 2 (SendGrid)
            │
            ├─→ Success → Return
            └─→ Failure → Log Error

Benefits:
✓ No single point of failure
✓ Automatic fallback
✓ Graceful degradation
✓ High reliability
```

## 🎛️ Dashboard Data Flow

```
GET /dashboard/stats
   │
   ▼
Dashboard Service
   │
   ├─→ Query: Today's bookings
   ├─→ Query: Upcoming bookings
   ├─→ Query: Conversations
   ├─→ Query: Form submissions
   ├─→ Query: Inventory items
   └─→ Query: Alerts
   │
   ▼
Aggregate Results
   │
   ├─→ Booking overview
   ├─→ Lead overview
   ├─→ Form overview
   ├─→ Inventory overview
   └─→ Alert summary
   │
   ▼
Return Dashboard Stats
```

## 🔄 Deployment Architecture

### Development

```
Developer Machine
   │
   ├─→ API Server (port 8000)
   ├─→ Celery Worker
   ├─→ Celery Beat
   └─→ Redis (local/Docker)
   │
   └─→ Supabase (cloud)
```

### Production

```
Internet
   │
   ▼
Load Balancer
   │
   ├─→ API Instance 1
   ├─→ API Instance 2
   └─→ API Instance 3
   │
   ├─→ Redis Cluster
   │   │
   │   ├─→ Celery Worker 1
   │   ├─→ Celery Worker 2
   │   └─→ Celery Beat
   │
   └─→ Supabase (managed)
```

## 📈 Scaling Strategy

### Horizontal Scaling

```
Small (< 1000 users)
   1 API instance
   1 Worker
   1 Beat
   Shared Redis

Medium (1000-10000 users)
   3 API instances
   3 Workers
   1 Beat
   Redis Cluster

Large (10000+ users)
   10+ API instances (auto-scale)
   10+ Workers (auto-scale)
   1 Beat
   Redis Cluster
   Read Replicas
```

## 🎯 Key Design Decisions

### 1. Why FastAPI?
- Async/await support
- Automatic API documentation
- Type hints and validation
- High performance
- Modern Python features

### 2. Why Supabase?
- PostgreSQL (reliable, powerful)
- Real-time capabilities
- Built-in authentication
- Row-level security
- Managed service

### 3. Why Celery?
- Distributed task queue
- Scheduled tasks (Beat)
- Retry logic
- Task monitoring
- Scalable

### 4. Why Multiple Providers?
- No single point of failure
- Automatic fallback
- Better reliability
- Cost optimization

### 5. Why Event-Driven?
- Decoupled components
- Easy to extend
- Predictable behavior
- Testable

## 🔍 Monitoring Points

```
┌─────────────────┐
│   API Metrics   │
├─────────────────┤
│ • Request rate  │
│ • Response time │
│ • Error rate    │
│ • Active users  │
└─────────────────┘

┌─────────────────┐
│  Task Metrics   │
├─────────────────┤
│ • Queue length  │
│ • Task duration │
│ • Success rate  │
│ • Retry count   │
└─────────────────┘

┌─────────────────┐
│   DB Metrics    │
├─────────────────┤
│ • Query time    │
│ • Connections   │
│ • Table size    │
│ • Index usage   │
└─────────────────┘

┌─────────────────┐
│ Business Metrics│
├─────────────────┤
│ • Bookings/day  │
│ • Messages sent │
│ • Forms filled  │
│ • Active spaces │
└─────────────────┘
```

## 🎓 Learning Resources

To understand this system better, study:

1. **FastAPI**: Official docs at fastapi.tiangolo.com
2. **Celery**: Distributed task queue concepts
3. **PostgreSQL**: Relational database design
4. **JWT**: Token-based authentication
5. **REST API**: RESTful design principles
6. **Async Python**: asyncio and async/await
7. **Docker**: Containerization basics
8. **SOLID**: Object-oriented design principles

---

**This overview provides a visual understanding of how all components work together to create a reliable, scalable operations platform.**
