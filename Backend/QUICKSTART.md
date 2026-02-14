# CareOps Backend - Quick Start Guide

Get up and running in 5 minutes!

## Prerequisites

- Python 3.11+
- Redis (or Docker)
- Supabase account

## Step 1: Clone & Setup (2 minutes)

```bash
cd Backend

# Copy environment template
cp .env.example .env

# Edit .env with your credentials
# Required: SUPABASE_URL, SUPABASE_KEY, SUPABASE_SERVICE_KEY
nano .env  # or use your favorite editor
```

## Step 2: Supabase Setup (2 minutes)

1. Go to [supabase.com](https://supabase.com) and create a project
2. In Supabase dashboard, go to SQL Editor
3. Copy contents of `supabase_schema.sql` and run it
4. Go to Settings > API and copy:
   - Project URL → `SUPABASE_URL`
   - anon public key → `SUPABASE_KEY`
   - service_role key → `SUPABASE_SERVICE_KEY`

## Step 3: Run (1 minute)

### Option A: Automated Script (Recommended)

```bash
chmod +x scripts/quick_start.sh
./scripts/quick_start.sh
```

### Option B: Docker

```bash
docker-compose up
```

### Option C: Manual

```bash
# Terminal 1: Install & Run API
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload

# Terminal 2: Run Celery Worker
celery -A app.tasks.celery_app worker --loglevel=info

# Terminal 3: Run Celery Beat
celery -A app.tasks.celery_app beat --loglevel=info
```

## Step 4: Test

Open http://localhost:8000/api/v1/docs

Try the health check:
```bash
curl http://localhost:8000/health
```

## Step 5: Create First User

```bash
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "owner@example.com",
    "password": "SecurePass123!",
    "full_name": "John Doe"
  }'
```

Save the `access_token` from the response!

## Step 6: Create Workspace

```bash
curl -X POST http://localhost:8000/api/v1/workspaces \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -d '{
    "name": "My Business",
    "address": "123 Main St",
    "timezone": "America/New_York",
    "contact_email": "contact@mybusiness.com"
  }'
```

## Next Steps

1. Configure email integration (Resend or SendGrid)
2. Set up booking types
3. Create forms
4. Add inventory items
5. Invite staff members

## Troubleshooting

### Redis not running?
```bash
# macOS
brew install redis
brew services start redis

# Ubuntu
sudo apt install redis-server
sudo systemctl start redis

# Docker
docker run -d -p 6379:6379 redis:alpine
```

### Supabase connection failed?
- Check URL and keys in `.env`
- Verify project is not paused
- Test connection: `python -c "from app.db.supabase_client import get_supabase_client; get_supabase_client()"`

### Import errors?
```bash
# Reinstall dependencies
pip install --upgrade -r requirements.txt
```

## What's Running?

- **API**: http://localhost:8000
- **Docs**: http://localhost:8000/api/v1/docs
- **Health**: http://localhost:8000/health
- **Redis**: localhost:6379

## Stop Services

```bash
# Docker
docker-compose down

# Manual
# Press Ctrl+C in each terminal
```

## Full Documentation

- [README.md](README.md) - Complete setup guide
- [API_DOCUMENTATION.md](API_DOCUMENTATION.md) - API reference
- [ARCHITECTURE.md](ARCHITECTURE.md) - System design
- [DEPLOYMENT.md](DEPLOYMENT.md) - Production deployment

## Need Help?

1. Check logs: `docker-compose logs` or terminal output
2. Review documentation
3. Test with Swagger UI: http://localhost:8000/api/v1/docs
4. Contact team lead

---

**You're ready to build! 🚀**
