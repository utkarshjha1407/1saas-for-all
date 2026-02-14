# CareOps Architecture Overview

## System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         USER BROWSER                             │
│                     http://localhost:8080                        │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             │ HTTP/REST API
                             │
┌────────────────────────────▼────────────────────────────────────┐
│                      FRONTEND (React)                            │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  Pages: Login, Dashboard, Bookings, Inbox, etc.         │  │
│  └──────────────────────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  React Query Hooks: useAuth, useDashboard, useBookings  │  │
│  └──────────────────────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  API Services: auth, workspace, booking, contact, etc.  │  │
│  └──────────────────────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  Axios Client: Interceptors, Token Refresh              │  │
│  └──────────────────────────────────────────────────────────┘  │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             │ JWT Token Auth
                             │
┌────────────────────────────▼────────────────────────────────────┐
│                    BACKEND (FastAPI)                             │
│                  http://localhost:8000                           │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  API Endpoints (40+)                                     │  │
│  │  - /auth/* (login, register, refresh)                   │  │
│  │  - /workspaces/* (CRUD)                                 │  │
│  │  - /bookings/* (CRUD, types, availability)             │  │
│  │  - /contacts/* (CRUD)                                   │  │
│  │  - /messages/* (conversations, messages)               │  │
│  │  - /forms/* (templates, submissions)                   │  │
│  │  - /inventory/* (items, usage, alerts)                 │  │
│  │  - /dashboard/* (stats, alerts)                        │  │
│  └──────────────────────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  Services Layer                                          │  │
│  │  - BookingService, WorkspaceService, etc.              │  │
│  └──────────────────────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  Security: JWT Auth, CORS, Rate Limiting               │  │
│  └──────────────────────────────────────────────────────────┘  │
└────────────────────────────┬────────────────────────────────────┘
                             │
                ┌────────────┴────────────┐
                │                         │
                ▼                         ▼
┌───────────────────────────┐  ┌──────────────────────────┐
│   SUPABASE (PostgreSQL)   │  │    REDIS (Cache/Queue)   │
│                           │  │                          │
│  Tables (13):             │  │  - Session Storage       │
│  - users                  │  │  - Celery Task Queue     │
│  - workspaces             │  │  - Rate Limiting         │
│  - contacts               │  │                          │
│  - bookings               │  └──────────────────────────┘
│  - booking_types          │
│  - availability_slots     │
│  - conversations          │
│  - messages               │
│  - form_templates         │
│  - form_submissions       │
│  - inventory_items        │
│  - inventory_usage        │
│  - alerts                 │
│  - integrations           │
│                           │
│  Features:                │
│  - Row Level Security     │
│  - Indexes & Constraints  │
│  - Triggers               │
└───────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                    BACKGROUND TASKS (Celery)                     │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  - Send booking confirmations                            │  │
│  │  - Send reminders (24h, 1h before)                      │  │
│  │  - Process form submissions                              │  │
│  │  - Check inventory levels                                │  │
│  │  - Generate alerts                                       │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│              EXTERNAL SERVICES (Integrations)                    │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  Email Providers:                                        │  │
│  │  - SendGrid (primary)                                    │  │
│  │  - Resend (fallback)                                     │  │
│  │                                                          │  │
│  │  SMS Provider:                                           │  │
│  │  - Twilio                                                │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

## Technology Stack

### Frontend
- **Framework**: React 18 with TypeScript
- **Build Tool**: Vite
- **UI Library**: shadcn/ui (Radix UI + Tailwind CSS)
- **State Management**: TanStack Query (React Query)
- **HTTP Client**: Axios with interceptors
- **Routing**: React Router v6
- **Animations**: Framer Motion
- **Forms**: React Hook Form + Zod validation

### Backend
- **Framework**: FastAPI (Python 3.9+)
- **Database**: PostgreSQL via Supabase
- **Authentication**: JWT tokens (PyJWT)
- **Task Queue**: Celery with Redis broker
- **Validation**: Pydantic v2
- **ORM**: Supabase Python Client
- **CORS**: FastAPI CORS middleware
- **Logging**: Structured logging with Python logging

### Infrastructure
- **Database**: Supabase (managed PostgreSQL)
- **Cache/Queue**: Redis (Docker)
- **Deployment**: Docker + Docker Compose
- **Environment**: .env files for configuration

## Data Flow

### Authentication Flow
```
1. User submits login form
   ↓
2. Frontend sends POST /auth/login
   ↓
3. Backend validates credentials
   ↓
4. Backend generates JWT tokens (access + refresh)
   ↓
5. Frontend stores tokens in localStorage
   ↓
6. Frontend includes token in Authorization header
   ↓
7. Backend validates token on each request
   ↓
8. If token expired, frontend auto-refreshes using refresh token
```

### Booking Creation Flow
```
1. User fills booking form
   ↓
2. Frontend validates data
   ↓
3. Frontend sends POST /bookings
   ↓
4. Backend validates business rules
   ↓
5. Backend creates booking in database
   ↓
6. Backend triggers Celery task
   ↓
7. Celery sends confirmation email/SMS
   ↓
8. Backend returns booking data
   ↓
9. Frontend updates UI with new booking
```

### Dashboard Data Flow
```
1. User navigates to dashboard
   ↓
2. Frontend calls useDashboard hook
   ↓
3. React Query fetches GET /dashboard/stats
   ↓
4. Backend queries database for stats
   ↓
5. Backend aggregates data (counts, alerts, etc.)
   ↓
6. Backend returns JSON response
   ↓
7. React Query caches response
   ↓
8. Frontend renders dashboard with data
```

## Security Architecture

### Authentication & Authorization
- JWT tokens with 30-minute expiration
- Refresh tokens for seamless re-authentication
- Role-based access control (Owner, Staff)
- Row Level Security (RLS) in Supabase

### API Security
- CORS configured for specific origins
- Rate limiting on sensitive endpoints
- Input validation with Pydantic
- SQL injection prevention via parameterized queries
- XSS prevention via React's built-in escaping

### Data Security
- Passwords hashed with bcrypt
- Sensitive data encrypted at rest (Supabase)
- HTTPS in production
- Environment variables for secrets
- No credentials in code

## Database Schema

### Core Tables
- **users**: User accounts with authentication
- **workspaces**: Business/organization data
- **contacts**: Customer/client information
- **bookings**: Appointment scheduling
- **booking_types**: Service definitions
- **availability_slots**: Staff availability

### Communication
- **conversations**: Message threads
- **messages**: Individual messages (email/SMS)

### Forms & Documents
- **form_templates**: Reusable form definitions
- **form_submissions**: Completed forms

### Inventory
- **inventory_items**: Stock tracking
- **inventory_usage**: Usage logs per booking

### System
- **alerts**: Notifications and warnings
- **integrations**: External service configs

## API Design

### RESTful Principles
- Resource-based URLs
- HTTP methods (GET, POST, PUT, DELETE)
- Status codes (200, 201, 400, 401, 404, 500)
- JSON request/response bodies

### Endpoint Structure
```
/api/v1/{resource}
  GET    /           - List all
  POST   /           - Create new
  GET    /{id}       - Get one
  PUT    /{id}       - Update
  DELETE /{id}       - Delete
```

### Response Format
```json
{
  "id": "uuid",
  "created_at": "2026-02-14T10:00:00Z",
  "updated_at": "2026-02-14T10:00:00Z",
  "...": "resource fields"
}
```

### Error Format
```json
{
  "detail": "Error message",
  "status_code": 400
}
```

## Deployment Architecture

### Development
- Backend: `uvicorn` with hot reload
- Frontend: `vite` dev server with HMR
- Database: Supabase cloud
- Redis: Docker container

### Production
- Backend: Docker container with gunicorn
- Frontend: Static files served by Nginx
- Database: Supabase production instance
- Redis: Managed Redis service
- Celery: Separate worker containers
- Load balancer: Nginx or cloud provider

## Scalability Considerations

### Current Capacity
- Single backend instance
- Supabase free tier (500MB, 2GB bandwidth)
- Redis single instance
- Suitable for: 1-100 concurrent users

### Scaling Options
1. **Horizontal Scaling**
   - Multiple backend instances behind load balancer
   - Redis cluster for high availability
   - Celery worker pool

2. **Database Scaling**
   - Supabase Pro plan (8GB, 50GB bandwidth)
   - Read replicas for queries
   - Connection pooling

3. **Caching**
   - Redis for frequently accessed data
   - CDN for static assets
   - Browser caching headers

4. **Optimization**
   - Database indexes on common queries
   - Lazy loading in frontend
   - Pagination for large lists
   - Background jobs for heavy tasks

## Monitoring & Observability

### Logging
- Structured JSON logs
- Log levels (DEBUG, INFO, WARNING, ERROR)
- Request/response logging
- Error tracking

### Metrics (Future)
- API response times
- Database query performance
- Error rates
- User activity

### Health Checks
- `/health` endpoint for backend
- Database connection check
- Redis connection check

## Development Workflow

### Local Development
1. Start Redis (Docker)
2. Start Backend (uvicorn)
3. Start Frontend (vite)
4. Make changes with hot reload

### Testing
- Backend: pytest
- Frontend: Vitest + React Testing Library
- E2E: (Future) Playwright

### Deployment
1. Build frontend: `npm run build`
2. Build backend Docker image
3. Push to container registry
4. Deploy to cloud provider
5. Run database migrations
6. Update environment variables

## Future Enhancements

### Planned Features
- Real-time notifications (WebSockets)
- File uploads (S3/Supabase Storage)
- Advanced analytics dashboard
- Mobile app (React Native)
- Multi-language support
- Calendar integrations (Google, Outlook)
- Payment processing (Stripe)
- Advanced reporting

### Technical Improvements
- GraphQL API option
- Microservices architecture
- Event-driven architecture
- Kubernetes deployment
- CI/CD pipeline
- Automated testing
- Performance monitoring
