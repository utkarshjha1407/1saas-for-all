# CareOps Backend

Production-ready FastAPI backend for the CareOps unified operations platform.

## Architecture

### Core Principles
- **SOLID Principles**: Clean separation of concerns with services, repositories, and controllers
- **No Single Point of Failure**: Multiple provider support with automatic fallback
- **Graceful Degradation**: System continues operating even if integrations fail
- **Event-Driven Automation**: Predictable, rule-based automation using Celery
- **Security First**: JWT authentication, RLS policies, input validation

### Tech Stack
- **Framework**: FastAPI (async, high-performance)
- **Database**: Supabase (PostgreSQL with real-time capabilities)
- **Task Queue**: Celery + Redis (background jobs, scheduled tasks)
- **Authentication**: JWT with role-based access control
- **Integrations**: Resend/SendGrid (email), Twilio (SMS)
- **Logging**: Structured logging with structlog
- **Monitoring**: Sentry integration ready

## Project Structure

```
Backend/
├── app/
│   ├── api/v1/              # API endpoints
│   │   └── endpoints/       # Route handlers
│   ├── core/                # Core configuration
│   │   ├── config.py        # Settings management
│   │   ├── security.py      # Auth & authorization
│   │   ├── exceptions.py    # Custom exceptions
│   │   └── logging_config.py
│   ├── db/                  # Database layer
│   │   └── supabase_client.py
│   ├── models/              # Data models
│   │   └── enums.py         # Enumerations
│   ├── schemas/             # Pydantic schemas
│   ├── services/            # Business logic
│   │   ├── base_service.py  # Base CRUD operations
│   │   ├── workspace_service.py
│   │   ├── booking_service.py
│   │   └── communication/   # Email & SMS providers
│   ├── tasks/               # Background tasks
│   │   ├── celery_app.py
│   │   └── automation_tasks.py
│   └── main.py              # Application entry point
├── supabase_schema.sql      # Database schema
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
└── .env.example
```

## Setup Instructions

### 1. Prerequisites
- Python 3.11+
- Docker & Docker Compose (optional)
- Supabase account
- Redis (for Celery)

### 2. Environment Setup

```bash
# Copy environment template
cp .env.example .env

# Edit .env with your credentials
```

### 3. Supabase Setup

1. Create a new Supabase project
2. Run the SQL schema:
   - Open Supabase SQL Editor
   - Copy contents of `supabase_schema.sql`
   - Execute the script

3. Get your credentials:
   - Project URL: `https://your-project.supabase.co`
   - Anon Key: From Settings > API
   - Service Role Key: From Settings > API (keep secret!)

### 4. Install Dependencies

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install packages
pip install -r requirements.txt
```

### 5. Run the Application

#### Option A: Docker (Recommended)
```bash
docker-compose up --build
```

#### Option B: Local Development
```bash
# Terminal 1: API Server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Terminal 2: Celery Worker
celery -A app.tasks.celery_app worker --loglevel=info

# Terminal 3: Celery Beat (Scheduler)
celery -A app.tasks.celery_app beat --loglevel=info
```

### 6. Access the API

- API Docs: http://localhost:8000/api/v1/docs
- ReDoc: http://localhost:8000/api/v1/redoc
- Health Check: http://localhost:8000/health

## API Endpoints

### Authentication
- `POST /api/v1/auth/register` - Register new user
- `POST /api/v1/auth/login` - Login
- `GET /api/v1/auth/me` - Get current user

### Workspaces
- `POST /api/v1/workspaces` - Create workspace
- `GET /api/v1/workspaces/{id}` - Get workspace
- `PATCH /api/v1/workspaces/{id}` - Update workspace
- `GET /api/v1/workspaces/{id}/onboarding` - Get onboarding status
- `POST /api/v1/workspaces/{id}/activate` - Activate workspace

### Bookings
- `POST /api/v1/bookings` - Create booking (public)
- `GET /api/v1/bookings` - List bookings
- `GET /api/v1/bookings/today` - Today's bookings
- `GET /api/v1/bookings/upcoming` - Upcoming bookings
- `PATCH /api/v1/bookings/{id}` - Update booking
- `POST /api/v1/bookings/{id}/status` - Update status

### Contacts
- `POST /api/v1/contacts` - Create contact (public)
- `GET /api/v1/contacts` - List contacts
- `GET /api/v1/contacts/{id}` - Get contact
- `PATCH /api/v1/contacts/{id}` - Update contact

### Messages
- `GET /api/v1/messages/conversations` - List conversations
- `GET /api/v1/messages/conversations/{id}/messages` - Get messages
- `POST /api/v1/messages/conversations/{id}/messages` - Send message
- `POST /api/v1/messages/conversations/{id}/mark-read` - Mark as read

### Forms
- `POST /api/v1/forms/templates` - Create form template
- `GET /api/v1/forms/templates` - List templates
- `POST /api/v1/forms/submissions` - Submit form (public)
- `GET /api/v1/forms/submissions` - List submissions

### Inventory
- `POST /api/v1/inventory` - Create item
- `GET /api/v1/inventory` - List items
- `GET /api/v1/inventory/low-stock` - Low stock items
- `PATCH /api/v1/inventory/{id}` - Update item
- `POST /api/v1/inventory/usage` - Record usage

### Dashboard
- `GET /api/v1/dashboard/stats` - Get dashboard statistics

### Integrations
- `POST /api/v1/integrations` - Create integration
- `GET /api/v1/integrations` - List integrations
- `DELETE /api/v1/integrations/{id}` - Delete integration

## Automation Rules

### Event-Based Triggers
1. **New Contact** → Send welcome message
2. **Booking Created** → Send confirmation + Send forms
3. **Before Booking** → Send reminder (24h before)
4. **Staff Reply** → Pause automation
5. **Form Pending 48h** → Mark overdue + Create alert
6. **Inventory Below Threshold** → Create alert

### Scheduled Tasks (Celery Beat)
- Check overdue forms: Every hour
- Send booking reminders: Every 30 minutes
- Check inventory levels: Every hour

## Security Features

- JWT-based authentication
- Role-based access control (Owner/Staff)
- Password hashing with bcrypt
- Row-level security (RLS) in Supabase
- Input validation with Pydantic
- CORS configuration
- Rate limiting ready
- SQL injection prevention

## Error Handling

- Custom exception hierarchy
- Graceful degradation for integrations
- Structured error logging
- Retry logic for external services
- Health checks for monitoring

## Testing

```bash
# Run tests
pytest

# With coverage
pytest --cov=app --cov-report=html
```

## Deployment

### Environment Variables (Production)
```bash
ENVIRONMENT=production
DEBUG=False
SECRET_KEY=<strong-random-key>
SUPABASE_URL=<your-supabase-url>
SUPABASE_KEY=<your-anon-key>
SUPABASE_SERVICE_KEY=<your-service-key>
# ... other credentials
```

### Docker Deployment
```bash
docker build -t careops-backend .
docker run -p 8000:8000 --env-file .env careops-backend
```

### Cloud Deployment Options
- **Render**: Connect GitHub repo, auto-deploy
- **Railway**: One-click deploy with Redis
- **Fly.io**: Global edge deployment
- **AWS ECS/Fargate**: Enterprise-grade
- **Google Cloud Run**: Serverless containers

## Monitoring & Logging

- Structured JSON logs in production
- Sentry integration for error tracking
- Health check endpoint for uptime monitoring
- Celery Flower for task monitoring (optional)

## Performance Optimization

- Connection pooling for Supabase
- Redis caching for frequently accessed data
- Database indexes on common queries
- Async/await for I/O operations
- GZip compression middleware
- Query optimization with proper joins

## Contributing

1. Follow SOLID principles
2. Write tests for new features
3. Use type hints
4. Document API changes
5. Keep services focused and single-purpose

## License

Proprietary - CareOps Hackathon Project
