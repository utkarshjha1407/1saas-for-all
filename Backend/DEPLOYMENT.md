# CareOps Backend Deployment Guide

## Quick Deploy Options

### 1. Render (Recommended for Hackathon)

**Pros**: Free tier, auto-deploy from GitHub, managed Redis
**Time**: ~10 minutes

#### Steps:

1. **Push to GitHub**
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git remote add origin <your-repo-url>
   git push -u origin main
   ```

2. **Create Render Account**
   - Go to [render.com](https://render.com)
   - Sign up with GitHub

3. **Deploy API**
   - Click "New +" → "Web Service"
   - Connect your repository
   - Settings:
     - Name: `careops-api`
     - Environment: `Python 3`
     - Build Command: `pip install -r requirements.txt`
     - Start Command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
     - Instance Type: Free
   - Add environment variables from `.env`
   - Click "Create Web Service"

4. **Deploy Redis**
   - Click "New +" → "Redis"
   - Name: `careops-redis`
   - Plan: Free
   - Copy the Internal Redis URL

5. **Deploy Celery Worker**
   - Click "New +" → "Background Worker"
   - Connect same repository
   - Settings:
     - Name: `careops-worker`
     - Build Command: `pip install -r requirements.txt`
     - Start Command: `celery -A app.tasks.celery_app worker --loglevel=info`
   - Add same environment variables
   - Update `REDIS_URL` with Internal Redis URL

6. **Deploy Celery Beat**
   - Repeat for Beat scheduler
   - Start Command: `celery -A app.tasks.celery_app beat --loglevel=info`

### 2. Railway

**Pros**: Simple, includes Redis, good free tier
**Time**: ~5 minutes

#### Steps:

1. Install Railway CLI
   ```bash
   npm i -g @railway/cli
   ```

2. Login and initialize
   ```bash
   railway login
   railway init
   ```

3. Add Redis
   ```bash
   railway add redis
   ```

4. Deploy
   ```bash
   railway up
   ```

5. Set environment variables
   ```bash
   railway variables set SUPABASE_URL=<your-url>
   railway variables set SUPABASE_KEY=<your-key>
   # ... add all variables
   ```

6. Get deployment URL
   ```bash
   railway domain
   ```

### 3. Fly.io

**Pros**: Global edge deployment, good performance
**Time**: ~15 minutes

#### Steps:

1. Install Fly CLI
   ```bash
   curl -L https://fly.io/install.sh | sh
   ```

2. Login
   ```bash
   fly auth login
   ```

3. Launch app
   ```bash
   fly launch
   ```

4. Add Redis
   ```bash
   fly redis create
   ```

5. Set secrets
   ```bash
   fly secrets set SUPABASE_URL=<your-url>
   fly secrets set SUPABASE_KEY=<your-key>
   # ... add all secrets
   ```

6. Deploy
   ```bash
   fly deploy
   ```

### 4. Docker + VPS (DigitalOcean, Linode, etc.)

**Pros**: Full control, cost-effective at scale
**Time**: ~30 minutes

#### Steps:

1. **Provision VPS**
   - Ubuntu 22.04 LTS
   - Minimum: 2GB RAM, 1 CPU

2. **Install Docker**
   ```bash
   curl -fsSL https://get.docker.com -o get-docker.sh
   sh get-docker.sh
   ```

3. **Clone repository**
   ```bash
   git clone <your-repo-url>
   cd Backend
   ```

4. **Configure environment**
   ```bash
   cp .env.example .env
   nano .env  # Edit with your credentials
   ```

5. **Deploy with Docker Compose**
   ```bash
   docker-compose up -d
   ```

6. **Setup Nginx reverse proxy**
   ```bash
   sudo apt install nginx
   sudo nano /etc/nginx/sites-available/careops
   ```

   ```nginx
   server {
       listen 80;
       server_name your-domain.com;

       location / {
           proxy_pass http://localhost:8000;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
       }
   }
   ```

   ```bash
   sudo ln -s /etc/nginx/sites-available/careops /etc/nginx/sites-enabled/
   sudo nginx -t
   sudo systemctl restart nginx
   ```

7. **Setup SSL with Let's Encrypt**
   ```bash
   sudo apt install certbot python3-certbot-nginx
   sudo certbot --nginx -d your-domain.com
   ```

## Environment Variables Checklist

Required for all deployments:

```bash
# Application
APP_NAME=CareOps
ENVIRONMENT=production
DEBUG=False
SECRET_KEY=<generate-strong-random-key>
API_VERSION=v1

# Supabase
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-anon-key
SUPABASE_SERVICE_KEY=your-service-role-key

# Redis
REDIS_URL=redis://localhost:6379/0

# Email (at least one)
RESEND_API_KEY=re_xxxxx
# OR
SENDGRID_API_KEY=SG.xxxxx

# SMS (optional)
TWILIO_ACCOUNT_SID=ACxxxxx
TWILIO_AUTH_TOKEN=xxxxx
TWILIO_PHONE_NUMBER=+1234567890

# Security
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7
ALGORITHM=HS256

# CORS
CORS_ORIGINS=https://your-frontend.com,https://www.your-frontend.com

# Monitoring (optional)
SENTRY_DSN=https://xxxxx@sentry.io/xxxxx
```

## Generate Secret Key

```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

## Post-Deployment Checklist

- [ ] API health check responds: `https://your-api.com/health`
- [ ] API docs accessible: `https://your-api.com/api/v1/docs`
- [ ] Can register new user
- [ ] Can create workspace
- [ ] Email integration working
- [ ] Celery tasks running (check logs)
- [ ] Database migrations applied
- [ ] SSL certificate active
- [ ] CORS configured for frontend
- [ ] Monitoring/logging active

## Monitoring

### Check API Health
```bash
curl https://your-api.com/health
```

### Check Celery Workers
```bash
# If using Docker
docker-compose logs celery-worker

# If using Render/Railway
# Check logs in dashboard
```

### Monitor with Sentry
1. Create Sentry account
2. Create new project (Python/FastAPI)
3. Add `SENTRY_DSN` to environment variables
4. Errors will be tracked automatically

## Scaling Considerations

### Horizontal Scaling
- Add more API instances behind load balancer
- Scale Celery workers independently
- Use managed Redis (Redis Cloud, AWS ElastiCache)

### Database Optimization
- Enable Supabase connection pooling
- Add database indexes (already in schema)
- Use read replicas for heavy queries

### Caching
- Add Redis caching layer
- Cache frequently accessed data
- Implement cache invalidation strategy

### CDN
- Use Cloudflare for API
- Cache static responses
- DDoS protection

## Troubleshooting

### API won't start
- Check environment variables
- Verify Supabase connection
- Check logs for errors

### Celery tasks not running
- Verify Redis connection
- Check worker logs
- Ensure beat scheduler is running

### Integration failures
- Verify API keys
- Check provider status pages
- Review error logs

### Performance issues
- Enable database query logging
- Check Celery queue length
- Monitor Redis memory usage
- Review Sentry performance metrics

## Backup Strategy

### Database
- Supabase automatic backups (daily)
- Manual backups via Supabase dashboard
- Export critical data regularly

### Environment Variables
- Store securely in password manager
- Document all required variables
- Keep backup of `.env` file (encrypted)

## Security Hardening

1. **Use strong SECRET_KEY**
2. **Enable HTTPS only**
3. **Configure CORS properly**
4. **Keep dependencies updated**
5. **Enable rate limiting**
6. **Monitor for vulnerabilities**
7. **Use environment-specific keys**
8. **Rotate credentials regularly**

## Cost Estimates (Monthly)

### Free Tier (Hackathon)
- Render: Free (750 hours)
- Supabase: Free (500MB, 2GB bandwidth)
- Redis: Free (25MB)
- **Total: $0**

### Production (Small)
- Render: $7/month (API)
- Render: $7/month (Worker)
- Supabase: $25/month (Pro)
- Redis Cloud: $5/month
- **Total: ~$44/month**

### Production (Medium)
- Railway: $20/month
- Supabase: $25/month
- Redis Cloud: $10/month
- **Total: ~$55/month**

## Support

For deployment issues:
1. Check logs first
2. Review this guide
3. Check provider documentation
4. Contact team lead

## Next Steps

After deployment:
1. Test all endpoints
2. Configure monitoring
3. Set up CI/CD pipeline
4. Document API for frontend team
5. Perform load testing
