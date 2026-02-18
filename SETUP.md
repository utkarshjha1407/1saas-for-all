# CareOps Setup Guide

## Prerequisites
- Python 3.9+
- Node.js 16+
- Supabase account

## Backend Setup

1. Navigate to Backend directory:
```bash
cd Backend
```

2. Create virtual environment:
```bash
python -m venv venv
```

3. Activate virtual environment:
```bash
# Windows
venv\Scripts\activate

# Mac/Linux
source venv/bin/activate
```

4. Install dependencies:
```bash
pip install -r requirements.txt
```

5. Configure environment:
- Copy `.env.example` to `.env`
- Update with your Supabase credentials

6. Run database migrations:
- Go to Supabase Dashboard > SQL Editor
- Run migrations from `Backend/migrations/` in order

7. Start backend:
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Or use the startup script:
```bash
start-backend.bat
```

Backend will be available at: http://localhost:8000
API Docs: http://localhost:8000/api/v1/docs

## Frontend Setup

1. Navigate to frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Start development server:
```bash
npm run dev
```

Frontend will be available at: http://localhost:8080

## Verification

1. Backend health check:
```bash
curl http://localhost:8000/health
```

2. Open frontend in browser:
```
http://localhost:8080
```

3. Login with test account or register new account

## Database Schema

The database includes tables for:
- Users and workspaces
- Contacts and conversations
- Bookings and booking types
- Availability schedules
- Forms and submissions
- Inventory management
- Alerts and analytics

All migrations are in `Backend/migrations/`

## Features

- User authentication and authorization
- Workspace management
- Contact management
- Booking system with availability
- Form builder and submissions
- Inventory tracking
- Real-time messaging
- Analytics and reporting

## Support

For issues:
1. Check backend logs
2. Check browser console
3. Verify database connection
4. Review API documentation at /api/v1/docs
