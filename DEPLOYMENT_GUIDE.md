# Deployment Guide

## 🎯 Recommended Architecture

```
Frontend (Vercel) → Backend (Railway/Render) → Database (Supabase)
```

## 1️⃣ Deploy Frontend to Vercel

### Prerequisites
- GitHub repository (✓ Already done)
- Vercel account (free)

### Steps

1. **Go to Vercel**
   - Visit: https://vercel.com
   - Sign up with GitHub

2. **Import Project**
   - Click "Add New Project"
   - Select your repository: `1saas-for-all`
   - Framework Preset: Vite
   - Root Directory: `frontend`

3. **Configure Build Settings**
   ```
   Build Command: npm run build
   Output Directory: dist
   Install Command: npm install
   ```

4. **Add Environment Variables**
   ```
   VITE_API_URL=https://your-backend-url.railway.app/api/v1
   ```

5. **Deploy**
   - Click "Deploy"
   - Wait 2-3 minutes
   - Get your URL: `https://your-app.vercel.app`

### Vercel Configuration File

Create `vercel.json` in root:
```json
{
  "buildCommand": "cd frontend && npm run build",
  "outputDirectory": "frontend/dist",
  "framework": "vite",
  "rewrites": [
    {
      "source": "/(.*)",
      "destination": "/index.html"
    }
  ]
}
```

## 2️⃣ Deploy Backend to Railway

### Prerequisites
- Railway account (free)
- GitHub repository

### Steps

1. **Go to Railway**
   - Visit: https://railway.app
   - Sign up with GitHub

2. **Create New Project**
   - Click "New Project"
   - Select "Deploy from GitHub repo"
   - Choose `1saas-for-all`

3. **Configure Service**
   - Root Directory: `Backend`
   - Start Command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

4. **Add Environment Variables**
   ```
   SUPABASE_URL=your_supabase_url
   SUPABASE_KEY=your_supabase_key
   SUPABASE_SERVICE_KEY=your_service_key
   SECRET_KEY=your_secret_key
   CORS_ORIGINS=https://your-app.vercel.app
   REDIS_URL=redis://redis:6379/0
   ENVIRONMENT=production
   ```

5. **Add Redis Service**
   - Click "New Service"
   - Select "Redis"
   - Railway will provide REDIS_URL automatically

6. **Deploy**
   - Railway auto-deploys on push
   - Get your URL: `https://your-app.railway.app`

### Railway Configuration

Create `railway.json` in Backend:
```json
{
  "build": {
    "builder": "NIXPACKS"
  },
  "deploy": {
    "startCommand": "uvicorn app.main:app --host 0.0.0.0 --port $PORT",
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 10
  }
}
```

Create `Procfile` in Backend:
```
web: uvicorn app.main:app --host 0.0.0.0 --port $PORT
worker: celery -A app.tasks.celery_app worker --loglevel=info
```

## 3️⃣ Alternative: Deploy Backend to Render

### Steps

1. **Go to Render**
   - Visit: https://render.com
   - Sign up with GitHub

2. **Create Web Service**
   - Click "New +"
   - Select "Web Service"
   - Connect GitHub repo

3. **Configure**
   ```
   Name: careops-backend
   Root Directory: Backend
   Environment: Python 3
   Build Command: pip install -r requirements.txt
   Start Command: uvicorn app.main:app --host 0.0.0.0 --port $PORT
   ```

4. **Add Environment Variables**
   (Same as Railway)

5. **Add Redis**
   - Create new Redis instance
   - Copy REDIS_URL to environment variables

## 4️⃣ Database (Supabase)

### Already Set Up! ✓

Just ensure:
1. All migrations are run
2. RLS policies are enabled
3. API keys are in environment variables

## 5️⃣ Update CORS

After deployment, update Backend CORS:

```python
# Backend/app/main.py
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:8080",
        "https://your-app.vercel.app",  # Add your Vercel URL
        "https://*.vercel.app",  # Allow preview deployments
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
    allow_headers=["*"],
)
```

## 6️⃣ Environment Variables Summary

### Frontend (.env.production)
```env
VITE_API_URL=https://your-backend.railway.app/api/v1
```

### Backend (Railway/Render)
```env
# Supabase
SUPABASE_URL=https://xxx.supabase.co
SUPABASE_KEY=your_anon_key
SUPABASE_SERVICE_KEY=your_service_key

# Security
SECRET_KEY=your_production_secret_key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# CORS
CORS_ORIGINS=https://your-app.vercel.app,https://*.vercel.app

# Redis
REDIS_URL=redis://redis:6379/0

# Email (Optional)
RESEND_API_KEY=your_key
SENDGRID_API_KEY=your_key

# SMS (Optional)
TWILIO_ACCOUNT_SID=your_sid
TWILIO_AUTH_TOKEN=your_token
TWILIO_PHONE_NUMBER=your_number

# Environment
ENVIRONMENT=production
DEBUG=False
```

## 7️⃣ Post-Deployment Checklist

- [ ] Frontend deployed to Vercel
- [ ] Backend deployed to Railway/Render
- [ ] Database migrations run on Supabase
- [ ] Environment variables configured
- [ ] CORS updated with production URLs
- [ ] Redis connected (for background tasks)
- [ ] Test authentication flow
- [ ] Test booking creation
- [ ] Test public booking page
- [ ] Custom domain configured (optional)
- [ ] SSL certificates active (automatic)

## 🔧 Continuous Deployment

Both Vercel and Railway auto-deploy on git push:

```bash
git add .
git commit -m "feat: your changes"
git push origin main
```

- Vercel: Deploys frontend automatically
- Railway: Deploys backend automatically

## 💰 Cost Estimate

### Free Tier Limits
- **Vercel**: 100GB bandwidth/month, unlimited projects
- **Railway**: $5 free credit/month (~500 hours)
- **Render**: 750 hours/month free
- **Supabase**: 500MB database, 2GB bandwidth

### Paid Plans (if needed)
- **Vercel Pro**: $20/month
- **Railway**: Pay as you go (~$5-20/month)
- **Render**: $7/month per service
- **Supabase Pro**: $25/month

## 🚨 Important Notes

1. **Environment Variables**: Never commit .env files
2. **Secret Keys**: Generate new ones for production
3. **CORS**: Update with actual production URLs
4. **Database**: Run all migrations before going live
5. **Monitoring**: Set up error tracking (Sentry)
6. **Backups**: Enable Supabase automatic backups

## 🔗 Useful Links

- Vercel Docs: https://vercel.com/docs
- Railway Docs: https://docs.railway.app
- Render Docs: https://render.com/docs
- Supabase Docs: https://supabase.com/docs

## 🆘 Troubleshooting

### Frontend not connecting to backend
- Check VITE_API_URL is correct
- Verify CORS settings in backend
- Check browser console for errors

### Backend not starting
- Check environment variables
- Verify Python version (3.9+)
- Check logs in Railway/Render dashboard

### Database connection issues
- Verify Supabase credentials
- Check if IP is whitelisted (Supabase allows all by default)
- Test connection from backend logs

## 📊 Monitoring

After deployment, monitor:
- Vercel Analytics (built-in)
- Railway/Render logs
- Supabase dashboard
- Error tracking (add Sentry)
