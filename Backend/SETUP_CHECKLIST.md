# CareOps Backend Setup Checklist

Use this checklist to ensure your backend is properly configured and running.

## ☐ Prerequisites

- [ ] Python 3.11+ installed
  ```bash
  python3 --version
  ```

- [ ] Git installed
  ```bash
  git --version
  ```

- [ ] Redis installed or Docker available
  ```bash
  redis-cli ping  # Should return PONG
  # OR
  docker --version
  ```

- [ ] Code editor (VS Code, PyCharm, etc.)

## ☐ Supabase Setup

- [ ] Created Supabase account at [supabase.com](https://supabase.com)
- [ ] Created new project
- [ ] Noted project name: _______________
- [ ] Copied Project URL to clipboard
- [ ] Copied anon public key to clipboard
- [ ] Copied service_role key to clipboard (⚠️ Keep secret!)
- [ ] Opened SQL Editor in Supabase dashboard
- [ ] Copied contents of `supabase_schema.sql`
- [ ] Executed SQL script successfully
- [ ] Verified tables created in Table Editor
- [ ] Checked for any SQL errors (should be none)

## ☐ Environment Configuration

- [ ] Navigated to Backend directory
  ```bash
  cd Backend
  ```

- [ ] Copied `.env.example` to `.env`
  ```bash
  cp .env.example .env
  ```

- [ ] Opened `.env` in editor
- [ ] Set `SUPABASE_URL` = (your project URL)
- [ ] Set `SUPABASE_KEY` = (your anon key)
- [ ] Set `SUPABASE_SERVICE_KEY` = (your service role key)
- [ ] Generated and set `SECRET_KEY`
  ```bash
  python3 -c "import secrets; print(secrets.token_urlsafe(32))"
  ```
- [ ] Set `ENVIRONMENT` = `development`
- [ ] Set `DEBUG` = `True`
- [ ] Configured at least one email provider:
  - [ ] Resend: Set `RESEND_API_KEY`
  - [ ] OR SendGrid: Set `SENDGRID_API_KEY`
- [ ] (Optional) Configured SMS:
  - [ ] Set `TWILIO_ACCOUNT_SID`
  - [ ] Set `TWILIO_AUTH_TOKEN`
  - [ ] Set `TWILIO_PHONE_NUMBER`
- [ ] Set `CORS_ORIGINS` for your frontend URL

## ☐ Python Environment

- [ ] Created virtual environment
  ```bash
  python3 -m venv venv
  ```

- [ ] Activated virtual environment
  ```bash
  # macOS/Linux
  source venv/bin/activate
  
  # Windows
  venv\Scripts\activate
  ```

- [ ] Verified activation (prompt shows `(venv)`)

- [ ] Upgraded pip
  ```bash
  pip install --upgrade pip
  ```

- [ ] Installed dependencies
  ```bash
  pip install -r requirements.txt
  ```

- [ ] Verified installation (no errors)

## ☐ Redis Setup

Choose one option:

### Option A: Local Redis
- [ ] Installed Redis
  ```bash
  # macOS
  brew install redis
  
  # Ubuntu
  sudo apt install redis-server
  ```

- [ ] Started Redis
  ```bash
  # macOS
  brew services start redis
  
  # Ubuntu
  sudo systemctl start redis
  ```

- [ ] Verified Redis is running
  ```bash
  redis-cli ping  # Should return PONG
  ```

### Option B: Docker Redis
- [ ] Started Redis container
  ```bash
  docker run -d -p 6379:6379 --name careops-redis redis:alpine
  ```

- [ ] Verified container is running
  ```bash
  docker ps | grep careops-redis
  ```

## ☐ Database Connection Test

- [ ] Tested Supabase connection
  ```bash
  python3 -c "from app.db.supabase_client import get_supabase_client; print('✓ Connected')"
  ```

- [ ] No errors displayed
- [ ] Saw "✓ Connected" message

## ☐ Run Tests

- [ ] Ran health check test
  ```bash
  pytest tests/test_health.py -v
  ```

- [ ] Test passed successfully
- [ ] No errors or warnings

## ☐ Start Services

### Option A: Quick Start Script (Recommended)
- [ ] Made script executable
  ```bash
  chmod +x scripts/quick_start.sh
  ```

- [ ] Ran quick start
  ```bash
  ./scripts/quick_start.sh
  ```

- [ ] All services started successfully

### Option B: Docker Compose
- [ ] Started with Docker Compose
  ```bash
  docker-compose up
  ```

- [ ] All containers running (api, celery-worker, celery-beat, redis)
- [ ] No error messages in logs

### Option C: Manual (3 terminals)
- [ ] Terminal 1: Started API server
  ```bash
  uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
  ```

- [ ] Terminal 2: Started Celery worker
  ```bash
  celery -A app.tasks.celery_app worker --loglevel=info
  ```

- [ ] Terminal 3: Started Celery beat
  ```bash
  celery -A app.tasks.celery_app beat --loglevel=info
  ```

- [ ] All services running without errors

## ☐ Verify Services

- [ ] API health check responds
  ```bash
  curl http://localhost:8000/health
  ```
  Expected: `{"status":"healthy","version":"v1"}`

- [ ] API docs accessible
  - Open: http://localhost:8000/api/v1/docs
  - [ ] Swagger UI loads
  - [ ] All endpoints visible

- [ ] ReDoc accessible
  - Open: http://localhost:8000/api/v1/redoc
  - [ ] Documentation loads

## ☐ Test API Endpoints

- [ ] Register new user
  ```bash
  curl -X POST http://localhost:8000/api/v1/auth/register \
    -H "Content-Type: application/json" \
    -d '{
      "email": "test@example.com",
      "password": "TestPass123!",
      "full_name": "Test User"
    }'
  ```

- [ ] Received access_token in response
- [ ] Saved token: _______________

- [ ] Login with user
  ```bash
  curl -X POST http://localhost:8000/api/v1/auth/login \
    -H "Content-Type: application/json" \
    -d '{
      "email": "test@example.com",
      "password": "TestPass123!"
    }'
  ```

- [ ] Login successful

- [ ] Create workspace
  ```bash
  curl -X POST http://localhost:8000/api/v1/workspaces \
    -H "Content-Type: application/json" \
    -H "Authorization: Bearer YOUR_TOKEN" \
    -d '{
      "name": "Test Business",
      "address": "123 Test St",
      "timezone": "America/New_York",
      "contact_email": "contact@test.com"
    }'
  ```

- [ ] Workspace created successfully
- [ ] Saved workspace_id: _______________

## ☐ Test Email Integration

- [ ] Configured email provider in `.env`
- [ ] Created test contact (triggers welcome email)
- [ ] Checked email provider dashboard
- [ ] Email sent successfully
- [ ] No errors in logs

## ☐ Test Background Tasks

- [ ] Checked Celery worker logs
- [ ] Worker connected to Redis
- [ ] No error messages

- [ ] Checked Celery beat logs
- [ ] Beat scheduler running
- [ ] Scheduled tasks visible

- [ ] Created test booking
- [ ] Confirmation email sent (check logs)
- [ ] Forms sent (check logs)

## ☐ Verify Database

- [ ] Opened Supabase dashboard
- [ ] Checked Table Editor
- [ ] Verified data in tables:
  - [ ] users table has test user
  - [ ] workspaces table has test workspace
  - [ ] contacts table (if created)
  - [ ] bookings table (if created)

## ☐ Check Logs

- [ ] API logs show no errors
- [ ] Celery worker logs show no errors
- [ ] Celery beat logs show no errors
- [ ] Redis logs show no errors (if applicable)

## ☐ Performance Check

- [ ] API responds quickly (< 1 second)
- [ ] No memory leaks visible
- [ ] CPU usage reasonable
- [ ] Database queries fast

## ☐ Documentation Review

- [ ] Read QUICKSTART.md
- [ ] Read README.md
- [ ] Reviewed API_DOCUMENTATION.md
- [ ] Checked ARCHITECTURE.md
- [ ] Reviewed DEPLOYMENT.md

## ☐ Development Tools

- [ ] Installed Postman or similar (optional)
- [ ] Imported OpenAPI spec (optional)
  - URL: http://localhost:8000/api/v1/openapi.json
- [ ] Created test collection (optional)

## ☐ Git Setup

- [ ] Initialized git repository
  ```bash
  git init
  ```

- [ ] Added remote
  ```bash
  git remote add origin <your-repo-url>
  ```

- [ ] Made initial commit
  ```bash
  git add .
  git commit -m "Initial commit: CareOps backend"
  ```

- [ ] Pushed to remote
  ```bash
  git push -u origin main
  ```

## ☐ Team Collaboration

- [ ] Shared repository with team
- [ ] Documented any custom setup steps
- [ ] Created team communication channel
- [ ] Scheduled sync meetings

## ☐ Next Steps

- [ ] Review business requirements
- [ ] Plan frontend integration
- [ ] Set up CI/CD pipeline (optional)
- [ ] Configure monitoring (optional)
- [ ] Plan deployment strategy

## 🎉 Setup Complete!

If all items are checked, your CareOps backend is ready for development!

## 🆘 Troubleshooting

### Common Issues

**Python version error**
- Install Python 3.11+ from python.org

**Redis connection failed**
- Check if Redis is running: `redis-cli ping`
- Restart Redis service
- Check `REDIS_URL` in `.env`

**Supabase connection failed**
- Verify credentials in `.env`
- Check if project is paused (free tier)
- Test connection in Supabase dashboard

**Import errors**
- Reinstall dependencies: `pip install -r requirements.txt`
- Check virtual environment is activated

**Port already in use**
- Change port: `uvicorn app.main:app --port 8001`
- Kill process using port: `lsof -ti:8000 | xargs kill`

**Email not sending**
- Verify API keys in `.env`
- Check provider dashboard
- Review error logs

### Getting Help

1. Check logs for error messages
2. Review documentation
3. Search GitHub issues
4. Ask team members
5. Contact project lead

## 📊 Setup Time Estimate

- Prerequisites: 10 minutes
- Supabase setup: 5 minutes
- Environment config: 5 minutes
- Python setup: 5 minutes
- Redis setup: 5 minutes
- Testing: 10 minutes

**Total: ~40 minutes** (first time)
**Subsequent setups: ~10 minutes**

---

**Ready to build something amazing! 🚀**
