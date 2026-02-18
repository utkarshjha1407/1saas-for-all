# CareOps - Unified Operations Platform

A complete full-stack application for managing service-based businesses with bookings, contact management, forms, inventory, and team collaboration.

## ✨ Features

- 🔐 User authentication with JWT
- 👥 Workspace and team management
- 📅 Booking system with availability scheduling
- 💬 Unified inbox for communications
- 📝 Contact management
- 📋 Form builder and submissions
- 📦 Inventory tracking with alerts
- 📊 Real-time dashboard analytics
- 🔔 Automated notifications

## 🚀 Quick Start

### Prerequisites
- Python 3.9+
- Node.js 16+
- Supabase account

### Backend Setup

1. Navigate to backend and create virtual environment:
```bash
cd Backend
python -m venv venv
```

2. Activate virtual environment:
```bash
# Windows
venv\Scripts\activate

# Mac/Linux
source venv/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Configure environment:
- Copy `.env.example` to `.env`
- Add your Supabase credentials

5. Run database migrations:
- Go to Supabase Dashboard > SQL Editor
- Run migrations from `Backend/migrations/` in order

6. Start backend:
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Backend: http://localhost:8000  
API Docs: http://localhost:8000/api/v1/docs

### Frontend Setup

1. Navigate to frontend:
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

Frontend: http://localhost:8080

## 📚 Documentation

- [Setup Guide](./SETUP.md) - Detailed setup instructions
- [Project Status](./PROJECT_STATUS.md) - Current implementation status
- [Backend README](./Backend/README.md) - Backend architecture
- [API Documentation](http://localhost:8000/api/v1/docs) - Interactive API docs

## 🏗️ Tech Stack

### Backend
- **Framework**: FastAPI (Python)
- **Database**: PostgreSQL (Supabase)
- **Authentication**: JWT with role-based access
- **Background Tasks**: Celery + Redis
- **Email/SMS**: Multi-provider support

### Frontend
- **Framework**: React 18 + TypeScript
- **Build Tool**: Vite
- **UI Components**: shadcn/ui
- **State Management**: TanStack Query
- **Styling**: Tailwind CSS
- **HTTP Client**: Axios

## 📁 Project Structure

```
careops/
├── Backend/              # FastAPI backend
│   ├── app/             # Application code
│   ├── tests/           # Test suite
│   ├── migrations/      # Database migrations
│   └── requirements.txt # Python dependencies
├── frontend/            # React frontend
│   ├── src/            # Source code
│   ├── public/         # Static assets
│   └── package.json    # Node dependencies
└── README.md           # This file
```

## 🔐 Environment Variables

### Backend (.env)
```env
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_anon_key
SUPABASE_SERVICE_KEY=your_service_key
SECRET_KEY=your_secret_key
CORS_ORIGINS=http://localhost:8080
```

### Frontend (.env)
```env
VITE_API_URL=http://localhost:8000/api/v1
```

## 🧪 Testing

### Backend Tests
```bash
cd Backend
pytest tests/ -v
```

### Frontend Tests
```bash
cd frontend
npm test
```

## 🚢 Deployment

1. Set up production environment variables
2. Run database migrations on production database
3. Build frontend: `npm run build`
4. Deploy backend with production ASGI server (e.g., Gunicorn)
5. Serve frontend build files with web server (e.g., Nginx)

## 📝 API Endpoints

Key endpoints:
- `POST /api/v1/auth/register` - User registration
- `POST /api/v1/auth/login` - User login
- `GET /api/v1/booking-types` - List booking types
- `POST /api/v1/bookings` - Create booking
- `GET /api/v1/contacts` - List contacts
- `GET /api/v1/dashboard/stats` - Dashboard statistics

Full API documentation: http://localhost:8000/api/v1/docs

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Write/update tests
5. Submit a pull request

## 📄 License

MIT License

## 🐛 Issues

Found a bug? Please open an issue on GitHub.

## 📞 Support

For questions and support, please open a GitHub issue or discussion.
