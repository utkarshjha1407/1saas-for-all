# CareOps Quick Reference

## 🚀 Start Commands

### Windows
```bash
# Start everything
start-dev.bat

# Or manually:
# Terminal 1 - Backend
cd Backend
venv\Scripts\activate
uvicorn app.main:app --reload --port 8000

# Terminal 2 - Frontend
cd frontend
npm run dev

# Terminal 3 - Celery (optional)
cd Backend
venv\Scripts\activate
celery -A app.tasks.celery_app worker --loglevel=info
```

### Mac/Linux
```bash
# Terminal 1 - Backend
cd Backend
source venv/bin/activate
uvicorn app.main:app --reload --port 8000

# Terminal 2 - Frontend
cd frontend
npm run dev

# Terminal 3 - Celery (optional)
cd Backend
source venv/bin/activate
celery -A app.tasks.celery_app worker --loglevel=info
```

## 🔗 URLs

- **Frontend**: http://localhost:8080
- **Backend**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **Redoc**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health

## 📁 Project Structure

```
careops/
├── Backend/                 # FastAPI backend
│   ├── app/
│   │   ├── api/v1/         # API endpoints
│   │   ├── core/           # Config, security
│   │   ├── db/             # Database client
│   │   ├── models/         # Data models
│   │   ├── schemas/        # Pydantic schemas
│   │   ├── services/       # Business logic
│   │   └── tasks/          # Celery tasks
│   ├── .env                # Environment variables
│   ├── requirements.txt    # Python dependencies
│   └── supabase_schema.sql # Database schema
├── frontend/               # React frontend
│   ├── src/
│   │   ├── components/     # UI components
│   │   ├── hooks/          # React hooks
│   │   ├── lib/api/        # API integration
│   │   ├── pages/          # Page components
│   │   └── App.tsx         # Main app
│   ├── .env                # Environment variables
│   └── package.json        # Node dependencies
└── README.md               # This file
```

## 🔑 Environment Variables

### Backend (.env)
```env
SUPABASE_URL=https://xxxxx.supabase.co
SUPABASE_KEY=eyJxxx...
SECRET_KEY=your-secret-key-here
CORS_ORIGINS=http://localhost:8080
REDIS_URL=redis://localhost:6379/0
```

### Frontend (.env)
```env
VITE_API_BASE_URL=http://localhost:8000
```

## 📡 API Endpoints

### Authentication
```
POST   /api/v1/auth/register      # Register new user
POST   /api/v1/auth/login         # Login
POST   /api/v1/auth/refresh       # Refresh token
GET    /api/v1/auth/me            # Get current user
```

### Workspaces
```
GET    /api/v1/workspaces         # List workspaces
POST   /api/v1/workspaces         # Create workspace
GET    /api/v1/workspaces/{id}    # Get workspace
PUT    /api/v1/workspaces/{id}    # Update workspace
```

### Bookings
```
GET    /api/v1/bookings           # List bookings
POST   /api/v1/bookings           # Create booking
GET    /api/v1/bookings/{id}      # Get booking
PUT    /api/v1/bookings/{id}      # Update booking
DELETE /api/v1/bookings/{id}      # Delete booking
```

### Contacts
```
GET    /api/v1/contacts           # List contacts
POST   /api/v1/contacts           # Create contact
GET    /api/v1/contacts/{id}      # Get contact
PUT    /api/v1/contacts/{id}      # Update contact
DELETE /api/v1/contacts/{id}      # Delete contact
```

### Dashboard
```
GET    /api/v1/dashboard/stats    # Get statistics
GET    /api/v1/dashboard/alerts   # Get alerts
```

## 🎣 React Hooks

### useAuth
```typescript
import { useAuth } from '@/hooks/useAuth';

const { login, logout, isLoading } = useAuth();

// Login
await login({ email, password });

// Logout
logout();
```

### useDashboard
```typescript
import { useDashboard } from '@/hooks/useDashboard';

const { data, isLoading, error } = useDashboard();

// data.stats - statistics
// data.alerts - alerts list
```

### useBookings
```typescript
import { useBookings } from '@/hooks/useBookings';

const { data: bookings, isLoading } = useBookings();

// bookings - array of booking objects
```

## 🛠️ Common Tasks

### Add New API Endpoint

1. **Backend** - Create endpoint in `Backend/app/api/v1/endpoints/`
```python
@router.get("/items")
async def get_items():
    return {"items": []}
```

2. **Frontend** - Add service in `frontend/src/lib/api/services/`
```typescript
export const itemService = {
  getAll: () => apiClient.get('/items'),
};
```

3. **Frontend** - Create hook in `frontend/src/hooks/`
```typescript
export const useItems = () => {
  return useQuery({
    queryKey: ['items'],
    queryFn: () => itemService.getAll(),
  });
};
```

### Add New Page

1. Create page in `frontend/src/pages/NewPage.tsx`
2. Add route in `frontend/src/App.tsx`
```typescript
<Route path="/new" element={<AppPage><NewPage /></AppPage>} />
```
3. Add nav item in `frontend/src/components/AppLayout.tsx`

### Add Database Table

1. Add SQL to `Backend/supabase_schema.sql`
2. Run in Supabase SQL Editor
3. Create Pydantic schema in `Backend/app/schemas/`
4. Create service in `Backend/app/services/`
5. Create endpoints in `Backend/app/api/v1/endpoints/`

## 🐛 Debug Commands

### Check Backend Health
```bash
curl http://localhost:8000/health
```

### Check Database Connection
```bash
cd Backend
python -c "from app.db.supabase_client import get_supabase_client; get_supabase_client()"
```

### Check Redis
```bash
redis-cli ping
# Should return: PONG
```

### View Backend Logs
```bash
# In terminal where uvicorn is running
# Logs appear automatically
```

### View Frontend Logs
```bash
# Open browser console (F12)
# Check Console tab
```

## 📦 Package Management

### Backend
```bash
# Install new package
pip install package-name

# Update requirements.txt
pip freeze > requirements.txt

# Install from requirements
pip install -r requirements.txt
```

### Frontend
```bash
# Install new package
npm install package-name

# Install dev dependency
npm install -D package-name

# Install from package.json
npm install
```

## 🧪 Testing

### Backend Tests
```bash
cd Backend
pytest
```

### Frontend Tests
```bash
cd frontend
npm test
```

## 🔒 Security Checklist

- [ ] SECRET_KEY is random and secure
- [ ] Supabase credentials are not in code
- [ ] CORS_ORIGINS is set correctly
- [ ] Passwords are hashed (bcrypt)
- [ ] JWT tokens expire (30 min)
- [ ] RLS policies are enabled
- [ ] Input validation on all endpoints
- [ ] HTTPS in production

## 📊 Database Tables

```
users               - User accounts
workspaces          - Business/organization
contacts            - Customers/clients
booking_types       - Service definitions
availability_slots  - Staff availability
bookings            - Appointments
conversations       - Message threads
messages            - Individual messages
form_templates      - Form definitions
form_submissions    - Completed forms
inventory_items     - Stock items
inventory_usage     - Usage logs
alerts              - Notifications
integrations        - External services
```

## 🎨 UI Components

All components from shadcn/ui are available:
- Button, Input, Label
- Card, Dialog, Sheet
- Table, Form, Select
- Toast, Alert, Badge
- And 30+ more...

Import from: `@/components/ui/component-name`

## 🔄 Git Workflow

```bash
# Check status
git status

# Add changes
git add .

# Commit
git commit -m "Description"

# Push
git push origin main
```

## 📝 Code Style

### Backend (Python)
- PEP 8 style guide
- Type hints everywhere
- Docstrings for functions
- Snake_case naming

### Frontend (TypeScript)
- ESLint rules
- Prettier formatting
- camelCase naming
- Functional components

## 🚀 Deployment

### Backend
```bash
# Build Docker image
docker build -t careops-backend .

# Run container
docker run -p 8000:8000 careops-backend
```

### Frontend
```bash
# Build for production
npm run build

# Output in dist/ folder
# Serve with Nginx or any static host
```

## 📞 Support

- Check [TROUBLESHOOTING.md](./TROUBLESHOOTING.md)
- Read [GETTING_STARTED.md](./GETTING_STARTED.md)
- Review [API_DOCUMENTATION.md](./Backend/API_DOCUMENTATION.md)

## 🎯 Quick Tips

1. Always activate venv before running backend
2. Check .env files are configured
3. Redis must be running for Celery
4. Clear browser cache if UI not updating
5. Check browser console for errors
6. Backend logs show detailed errors
7. Use API docs at /docs for testing
8. React Query DevTools for debugging
9. Supabase dashboard for database
10. Keep documentation updated!
