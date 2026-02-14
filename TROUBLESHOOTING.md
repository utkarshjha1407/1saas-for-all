# CareOps Troubleshooting Guide

## Common Issues and Solutions

### Backend Issues

#### 1. "Module not found" errors
**Problem**: Missing Python packages
**Solution**:
```bash
cd Backend
pip install -r requirements.txt
```

#### 2. Supabase connection errors
**Problem**: Invalid Supabase credentials
**Solution**:
- Check `Backend/.env` file
- Verify `SUPABASE_URL` and `SUPABASE_KEY` are correct
- Test connection:
```bash
python -c "from app.db.supabase_client import get_supabase_client; client = get_supabase_client(); print('✅ Connected!')"
```

#### 3. Redis connection errors
**Problem**: Redis not running
**Solution**:
```bash
# Start Redis with Docker
docker run -d -p 6379:6379 --name careops-redis redis:alpine

# Or check if it's already running
docker ps | findstr redis
```

#### 4. CORS errors
**Problem**: Frontend can't connect to backend
**Solution**:
- Check `Backend/.env` has: `CORS_ORIGINS=http://localhost:8080`
- Restart backend after changing .env

#### 5. Port already in use
**Problem**: Port 8000 is occupied
**Solution**:
```bash
# Windows
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# Or use a different port
uvicorn app.main:app --reload --port 8001
```

### Frontend Issues

#### 1. "Cannot find module" errors
**Problem**: Missing npm packages
**Solution**:
```bash
cd frontend
npm install
```

#### 2. API connection errors
**Problem**: Frontend can't reach backend
**Solution**:
- Check `frontend/.env` has: `VITE_API_BASE_URL=http://localhost:8000`
- Verify backend is running on port 8000
- Check browser console for CORS errors

#### 3. Login not working
**Problem**: Authentication fails
**Solution**:
- Check backend is running
- Verify Supabase database has users table
- Check browser console for error messages
- Clear localStorage: `localStorage.clear()`

#### 4. "Blank page" or "White screen"
**Problem**: Build or runtime error
**Solution**:
- Check browser console for errors
- Restart frontend dev server
- Clear browser cache
- Try incognito/private mode

#### 5. Port 8080 already in use
**Problem**: Another app using port 8080
**Solution**:
```bash
# Edit vite.config.ts to use different port
server: {
  port: 3000,
  host: true
}
```

### Database Issues

#### 1. Tables not found
**Problem**: Database schema not created
**Solution**:
- Go to Supabase dashboard
- Open SQL Editor
- Run `Backend/supabase_schema.sql`
- Verify all 13 tables are created

#### 2. Permission denied errors
**Problem**: Row Level Security (RLS) blocking access
**Solution**:
- Check RLS policies in Supabase
- Verify JWT token is valid
- Check user has correct workspace_id

#### 3. Foreign key constraint errors
**Problem**: Trying to create records with invalid references
**Solution**:
- Ensure referenced records exist first
- Check workspace_id matches user's workspace
- Verify contact_id exists before creating booking

### Authentication Issues

#### 1. Token expired errors
**Problem**: JWT token has expired
**Solution**:
- Frontend should auto-refresh tokens
- If not working, logout and login again
- Check `ACCESS_TOKEN_EXPIRE_MINUTES` in backend .env

#### 2. "Unauthorized" on protected routes
**Problem**: No valid token in localStorage
**Solution**:
```javascript
// Check in browser console
console.log(localStorage.getItem('access_token'))

// If null, login again
```

#### 3. Can't register new users
**Problem**: Email already exists or validation error
**Solution**:
- Use a different email
- Check password is at least 6 characters
- Verify all required fields are filled

### Development Issues

#### 1. Changes not reflecting
**Problem**: Hot reload not working
**Solution**:
- Restart dev server
- Clear browser cache
- Check file is saved
- Verify no syntax errors

#### 2. TypeScript errors
**Problem**: Type mismatches
**Solution**:
```bash
# Check types
cd frontend
npm run build

# Fix common issues
- Import types from @/lib/api/types
- Use 'any' temporarily for complex types
```

#### 3. Celery tasks not running
**Problem**: Background tasks not executing
**Solution**:
- Check Redis is running
- Start Celery worker:
```bash
cd Backend
celery -A app.tasks.celery_app worker --loglevel=info
```

## Quick Diagnostics

### Check Backend Health
```bash
curl http://localhost:8000/health
# Should return: {"status":"healthy"}
```

### Check Frontend Build
```bash
cd frontend
npm run build
# Should complete without errors
```

### Check Database Connection
```bash
cd Backend
python -c "from app.db.supabase_client import get_supabase_client; get_supabase_client()"
# Should not throw errors
```

### Check Redis Connection
```bash
redis-cli ping
# Should return: PONG
```

## Environment Variables Checklist

### Backend (.env)
- [ ] SUPABASE_URL is set
- [ ] SUPABASE_KEY is set
- [ ] SECRET_KEY is set (generate with: `python -c "import secrets; print(secrets.token_urlsafe(32))"`)
- [ ] CORS_ORIGINS includes frontend URL
- [ ] REDIS_URL is correct

### Frontend (.env)
- [ ] VITE_API_BASE_URL points to backend

## Getting Help

If you're still stuck:

1. **Check logs**:
   - Backend: Terminal where uvicorn is running
   - Frontend: Browser console (F12)
   - Redis: `docker logs careops-redis`

2. **Verify versions**:
   ```bash
   python --version  # Should be 3.9+
   node --version    # Should be 18+
   npm --version
   ```

3. **Clean restart**:
   ```bash
   # Stop everything
   # Delete node_modules and venv
   # Reinstall dependencies
   # Start fresh
   ```

4. **Check documentation**:
   - [Backend README](./Backend/README.md)
   - [API Documentation](./Backend/API_DOCUMENTATION.md)
   - [Integration Guide](./frontend/INTEGRATION_GUIDE.md)

## Common Error Messages

### "Failed to fetch"
- Backend not running
- Wrong API URL in frontend .env
- CORS not configured

### "Network Error"
- Backend crashed
- Port blocked by firewall
- Wrong URL

### "401 Unauthorized"
- Not logged in
- Token expired
- Invalid credentials

### "403 Forbidden"
- User doesn't have permission
- Wrong workspace_id
- RLS policy blocking

### "404 Not Found"
- Wrong API endpoint
- Resource doesn't exist
- Typo in URL

### "500 Internal Server Error"
- Backend error (check logs)
- Database connection issue
- Unhandled exception

## Performance Issues

### Slow API responses
- Check database indexes
- Verify Supabase plan limits
- Check network latency

### High memory usage
- Restart services
- Check for memory leaks
- Reduce concurrent requests

### Slow frontend loading
- Run production build: `npm run build`
- Check bundle size
- Optimize images

## Reset Everything

If all else fails, complete reset:

```bash
# 1. Stop all services
# 2. Delete databases (Supabase dashboard)
# 3. Delete Redis data
docker rm -f careops-redis

# 4. Clean backend
cd Backend
rmdir /s venv
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt

# 5. Clean frontend
cd frontend
rmdir /s node_modules
npm install

# 6. Recreate database
# Run supabase_schema.sql in Supabase

# 7. Start fresh
# Use start-dev.bat
```
