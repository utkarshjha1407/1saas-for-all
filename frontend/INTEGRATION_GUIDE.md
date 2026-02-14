# Frontend-Backend Integration Guide

## 🎯 Overview

This guide explains how the CareOps frontend connects to the FastAPI backend following industry best practices.

## 📁 Architecture

```
frontend/src/
├── lib/api/                    # API Layer
│   ├── client.ts              # Axios client with interceptors
│   ├── types.ts               # TypeScript interfaces
│   ├── services/              # API service modules
│   │   ├── auth.service.ts
│   │   ├── workspace.service.ts
│   │   ├── booking.service.ts
│   │   ├── contact.service.ts
│   │   ├── dashboard.service.ts
│   │   └── message.service.ts
│   └── index.ts               # Central export
│
└── hooks/                      # React Query hooks
    ├── useAuth.ts
    ├── useWorkspace.ts
    ├── useBookings.ts
    └── useDashboard.ts
```

## 🔧 Setup

### 1. Install Dependencies

```bash
cd frontend
npm install axios
```

### 2. Configure Environment

Already configured in `.env`:
```env
VITE_API_URL=http://localhost:8000/api/v1
VITE_API_BASE_URL=http://localhost:8000
```

### 3. Start Both Services

**Terminal 1 - Backend:**
```bash
cd Backend
venv\Scripts\activate
uvicorn app.main:app --reload --port 8000
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm run dev
```

## 🔐 Authentication Flow

### 1. Login Example

```typescript
import { useAuth } from '@/hooks/useAuth';

function LoginPage() {
  const { login, isLoginLoading } = useAuth();

  const handleLogin = () => {
    login({
      email: 'user@example.com',
      password: 'password123'
    });
  };

  return (
    <button onClick={handleLogin} disabled={isLoginLoading}>
      {isLoginLoading ? 'Logging in...' : 'Login'}
    </button>
  );
}
```

### 2. Protected Routes

```typescript
import { Navigate } from 'react-router-dom';
import { useAuth } from '@/hooks/useAuth';

function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const { isAuthenticated, isLoading } = useAuth();

  if (isLoading) return <div>Loading...</div>;
  if (!isAuthenticated) return <Navigate to="/login" />;

  return <>{children}</>;
}
```

### 3. Automatic Token Management

The API client automatically:
- ✅ Adds Bearer token to all requests
- ✅ Refreshes expired tokens
- ✅ Redirects to login on auth failure
- ✅ Handles 401 errors globally

## 📊 Data Fetching Examples

### Dashboard Statistics

```typescript
import { useDashboard } from '@/hooks/useDashboard';

function Dashboard() {
  const { stats, isLoading, refetch } = useDashboard();

  if (isLoading) return <div>Loading...</div>;

  return (
    <div>
      <h1>Today's Bookings: {stats?.bookings.today_count}</h1>
      <h2>Pending Forms: {stats?.forms.pending_count}</h2>
      <button onClick={() => refetch()}>Refresh</button>
    </div>
  );
}
```

### Create Booking

```typescript
import { useBookings } from '@/hooks/useBookings';

function BookingForm() {
  const { createBooking, isCreating } = useBookings();

  const handleSubmit = (data) => {
    createBooking({
      data: {
        booking_type_id: 'uuid',
        contact_name: 'John Doe',
        contact_email: 'john@example.com',
        scheduled_at: '2024-02-15T14:00:00Z',
      },
      workspaceId: 'workspace-uuid'
    });
  };

  return (
    <form onSubmit={handleSubmit}>
      {/* Form fields */}
      <button type="submit" disabled={isCreating}>
        {isCreating ? 'Creating...' : 'Create Booking'}
      </button>
    </form>
  );
}
```

### Workspace Management

```typescript
import { useWorkspace } from '@/hooks/useWorkspace';

function WorkspaceSettings() {
  const { workspace, onboardingStatus, isLoading } = useWorkspace('workspace-id');

  if (isLoading) return <div>Loading...</div>;

  return (
    <div>
      <h1>{workspace?.name}</h1>
      <p>Status: {workspace?.status}</p>
      <p>Onboarding: {onboardingStatus?.current_step}</p>
    </div>
  );
}
```

## 🔄 API Client Features

### Automatic Request Interceptor

```typescript
// Automatically adds to every request:
headers: {
  'Authorization': 'Bearer <access_token>',
  'Content-Type': 'application/json'
}
```

### Automatic Response Interceptor

```typescript
// Handles:
- 401 Unauthorized → Auto token refresh
- 403 Forbidden → Show error
- 500 Server Error → Show error
- Network errors → Show error
```

### Error Handling

```typescript
try {
  const data = await bookingService.create(bookingData, workspaceId);
  toast.success('Booking created!');
} catch (error) {
  // Error is already formatted by interceptor
  toast.error(error.message);
}
```

## 📝 TypeScript Types

All API responses are fully typed:

```typescript
import { Booking, Workspace, User } from '@/lib/api';

const booking: Booking = {
  id: 'uuid',
  workspace_id: 'uuid',
  booking_type_id: 'uuid',
  contact_id: 'uuid',
  scheduled_at: '2024-02-15T14:00:00Z',
  status: 'confirmed',
  created_at: '2024-02-14T10:00:00Z',
  updated_at: '2024-02-14T10:00:00Z'
};
```

## 🎣 React Query Integration

### Benefits

- ✅ Automatic caching
- ✅ Background refetching
- ✅ Optimistic updates
- ✅ Loading & error states
- ✅ Automatic retries

### Query Keys

```typescript
['currentUser']                    // Current user
['workspace', workspaceId]         // Specific workspace
['bookings']                       // All bookings
['bookings', 'today']              // Today's bookings
['dashboardStats']                 // Dashboard data
```

### Invalidation

```typescript
// After creating a booking, invalidate queries:
queryClient.invalidateQueries({ queryKey: ['bookings'] });
```

## 🚀 Usage Examples

### Complete Login Flow

```typescript
import { useAuth } from '@/hooks/useAuth';
import { useForm } from 'react-hook-form';

function LoginPage() {
  const { login, isLoginLoading } = useAuth();
  const { register, handleSubmit } = useForm();

  const onSubmit = (data) => {
    login(data); // Automatically redirects on success
  };

  return (
    <form onSubmit={handleSubmit(onSubmit)}>
      <input {...register('email')} type="email" required />
      <input {...register('password')} type="password" required />
      <button type="submit" disabled={isLoginLoading}>
        {isLoginLoading ? 'Logging in...' : 'Login'}
      </button>
    </form>
  );
}
```

### Complete Dashboard

```typescript
import { useDashboard } from '@/hooks/useDashboard';
import { useBookings } from '@/hooks/useBookings';

function DashboardPage() {
  const { stats, isLoading: statsLoading } = useDashboard();
  const { todayBookings, isLoading: bookingsLoading } = useBookings();

  if (statsLoading || bookingsLoading) {
    return <div>Loading dashboard...</div>;
  }

  return (
    <div>
      <h1>Dashboard</h1>
      
      {/* Stats Cards */}
      <div className="grid grid-cols-4 gap-4">
        <Card>
          <h3>Today's Bookings</h3>
          <p>{stats?.bookings.today_count}</p>
        </Card>
        <Card>
          <h3>Pending Forms</h3>
          <p>{stats?.forms.pending_count}</p>
        </Card>
        <Card>
          <h3>Low Stock Items</h3>
          <p>{stats?.inventory.low_stock_items}</p>
        </Card>
        <Card>
          <h3>Alerts</h3>
          <p>{stats?.total_alerts}</p>
        </Card>
      </div>

      {/* Today's Bookings List */}
      <div className="mt-8">
        <h2>Today's Bookings</h2>
        {todayBookings?.map(booking => (
          <BookingCard key={booking.id} booking={booking} />
        ))}
      </div>
    </div>
  );
}
```

## 🔍 Testing the Integration

### 1. Test Health Check

```bash
curl http://localhost:8000/health
```

### 2. Test Registration

```typescript
// In browser console:
import { authService } from '@/lib/api';

authService.register({
  email: 'test@example.com',
  password: 'SecurePass123!',
  full_name: 'Test User'
});
```

### 3. Test API Call

```typescript
// In browser console:
import { dashboardService } from '@/lib/api';

const stats = await dashboardService.getStats();
console.log(stats);
```

## 🐛 Troubleshooting

### CORS Errors

Backend already configured with CORS. If issues persist:

```python
# Backend/app/core/config.py
CORS_ORIGINS: str = "http://localhost:8080,http://localhost:5173"
```

### 401 Unauthorized

- Check if token is stored: `localStorage.getItem('access_token')`
- Check if backend is running: `http://localhost:8000/health`
- Check token expiration

### Network Errors

- Verify backend URL in `.env`
- Check if backend is running
- Check browser console for errors

## 📚 Best Practices

1. **Always use hooks** - Don't call services directly in components
2. **Handle loading states** - Show spinners/skeletons
3. **Handle errors** - Show user-friendly messages
4. **Type everything** - Use TypeScript interfaces
5. **Invalidate queries** - After mutations
6. **Use optimistic updates** - For better UX
7. **Cache strategically** - Balance freshness vs performance

## 🎉 You're Ready!

The frontend is now fully integrated with the backend using:
- ✅ Axios for HTTP requests
- ✅ React Query for data fetching
- ✅ TypeScript for type safety
- ✅ Automatic token management
- ✅ Global error handling
- ✅ Custom hooks for each feature

Start building your UI components and they'll automatically connect to the backend!
