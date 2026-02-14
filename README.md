# CareOps - Unified Operations Platform

A complete full-stack application for managing service-based businesses with bookings, messaging, forms, inventory, and team management.

## 🎯 Quick Links

- **[🚀 Getting Started Guide](./GETTING_STARTED.md)** - Start here! Complete setup in 10 minutes
- **[📍 Current State](./CURRENT_STATE.md)** - What works right now (detailed status)
- **[🎨 Visual Walkthrough](./VISUAL_WALKTHROUGH.md)** - See the UI and user experience
- **[⚡ Quick Reference](./QUICK_REFERENCE.md)** - Commands, URLs, and code snippets
- **[📊 What We Built](./WHAT_WE_BUILT.md)** - Complete project summary
- **[✅ Project Status](./PROJECT_STATUS.md)** - Implementation progress
- **[🏗️ Architecture Overview](./ARCHITECTURE_OVERVIEW.md)** - System design and diagrams
- **[🔧 Troubleshooting](./TROUBLESHOOTING.md)** - Fix common issues
- **[📚 Backend Documentation](./Backend/README.md)** - Backend architecture
- **[📖 API Reference](./Backend/API_DOCUMENTATION.md)** - Complete API docs
- **[🔌 Integration Guide](./frontend/INTEGRATION_GUIDE.md)** - Frontend API usage

## ✨ What's Working Right Now

You can immediately:
- ✅ Register and create a workspace
- ✅ Login with authentication
- ✅ View dashboard with real-time stats
- ✅ Manage bookings from the database
- ✅ Navigate between all pages
- ✅ Secure logout

## 🚀 Quick Start

### Prerequisites
- Python 3.9+
- Node.js 18+
- Redis (Docker or local)
- Supabase account

### Backend Setup

1. Navigate to backend directory:
```bash
cd Backend
```

2. Create and activate virtual environment:
```bash
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # Mac/Linux
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Configure environment variables (copy `.env.example` to `.env` and fill in):
```env
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_anon_key
SECRET_KEY=your_secret_key
CORS_ORIGINS=http://localhost:8080
```

5. Start Redis (if using Docker):
```bash
docker run -d -p 6379:6379 --name careops-redis redis:alpine
```

6. Run the backend:
```bash
uvicorn app.main:app --reload --port 8000
```

Backend will be available at: http://localhost:8000

### Frontend Setup

1. Navigate to frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Configure environment variables (copy `.env.example` to `.env`):
```env
VITE_API_BASE_URL=http://localhost:8000
```

4. Start the development server:
```bash
npm run dev
```

Frontend will be available at: http://localhost:8080

## 📚 Documentation

- [Backend README](./Backend/README.md) - Backend architecture and API docs
- [API Documentation](./Backend/API_DOCUMENTATION.md) - Complete API reference
- [Frontend Integration Guide](./frontend/INTEGRATION_GUIDE.md) - How to use the API layer
- [Project Status](./PROJECT_STATUS.md) - Current implementation status

## 🏗️ Architecture

### Backend (FastAPI + Supabase)
- **Framework**: FastAPI with async support
- **Database**: PostgreSQL via Supabase
- **Authentication**: JWT tokens with role-based access
- **Background Tasks**: Celery with Redis
- **Communication**: Multi-provider (SendGrid, Resend, Twilio)

### Frontend (React + TypeScript)
- **Framework**: Vite + React 18
- **UI Library**: shadcn/ui components
- **State Management**: React Query (TanStack Query)
- **Routing**: React Router v6
- **Styling**: Tailwind CSS

## 🎯 Features

### Core Functionality
- ✅ User authentication and authorization
- ✅ Workspace management
- ✅ Booking system with calendar
- ✅ Unified inbox (email + SMS)
- ✅ Contact management
- ✅ Form templates and submissions
- ✅ Inventory tracking with alerts
- ✅ Dashboard with real-time stats
- ✅ Team management with permissions

### API Integration
- ✅ Axios client with interceptors
- ✅ Automatic token refresh
- ✅ React Query hooks for data fetching
- ✅ TypeScript interfaces for type safety

## 🔐 Default Credentials

After registration, you can login with your created account.

## 📦 Tech Stack

**Backend:**
- FastAPI
- Supabase (PostgreSQL)
- Celery + Redis
- Pydantic
- JWT Authentication

**Frontend:**
- React 18
- TypeScript
- Vite
- TanStack Query
- Axios
- shadcn/ui
- Tailwind CSS
- Framer Motion

## 🛠️ Development

### Backend Development
```bash
cd Backend
uvicorn app.main:app --reload --port 8000
```

### Frontend Development
```bash
cd frontend
npm run dev
```

### Run Tests
```bash
# Backend tests
cd Backend
pytest

# Frontend tests
cd frontend
npm test
```

## 📝 Environment Variables

### Backend (.env)
```env
# Supabase
SUPABASE_URL=
SUPABASE_KEY=

# Security
SECRET_KEY=
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# CORS
CORS_ORIGINS=http://localhost:8080

# Redis
REDIS_URL=redis://localhost:6379/0

# Email Providers
SENDGRID_API_KEY=
RESEND_API_KEY=

# SMS Provider
TWILIO_ACCOUNT_SID=
TWILIO_AUTH_TOKEN=
TWILIO_PHONE_NUMBER=
```

### Frontend (.env)
```env
VITE_API_BASE_URL=http://localhost:8000
```

## 🚢 Deployment

See [DEPLOYMENT.md](./Backend/DEPLOYMENT.md) for production deployment instructions.

## 📄 License

MIT License - see LICENSE file for details

## 🤝 Contributing

See [CONTRIBUTING.md](./Backend/CONTRIBUTING.md) for contribution guidelines.

## 📞 Support

For issues and questions, please open a GitHub issue.
