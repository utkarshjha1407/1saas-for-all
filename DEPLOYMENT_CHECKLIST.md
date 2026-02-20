# Deployment Checklist

## ✅ Pre-Deployment

- [ ] Code pushed to GitHub
- [ ] Database migrations ready
- [ ] Environment variables documented
- [ ] SECRET_KEY generated for production

## 🚀 Railway Backend Deployment

### 1. Create Project
- [ ] Go to https://railway.app
- [ ] Sign in with GitHub
- [ ] Click "New Project"
- [ ] Select "Deploy from GitHub repo"
- [ ] Choose `1saas-for-all` repository

### 2. Configure Service
- [ ] Click on the service
- [ ] Go to "Settings" tab
- [ ] Set "Root Directory" to: `Backend`
- [ ] Set "Start Command" to: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

### 3. Add Environment Variables
Go to "Variables" tab and add:

**Required:**
- [ ] `SUPABASE_URL` = `https://mriwhoavwsncxsozgmeb.supabase.co`
- [ ] `SUPABASE_KEY` = (your anon key)
- [ ] `SUPABASE_SERVICE_KEY` = (your service role key)
- [ ] `SECRET_KEY` = (generate new random key)
- [ ] `CORS_ORIGINS` = `https://your-app.vercel.app`
- [ ] `ENVIRONMENT` = `production`
- [ ] `DEBUG` = `False`

**Optional (for email/SMS):**
- [ ] `RESEND_API_KEY` = (if using Resend)
- [ ] `SENDGRID_API_KEY` = (if using SendGrid)
- [ ] `TWILIO_ACCOUNT_SID` = (if using Twilio)
- [ ] `TWILIO_AUTH_TOKEN` = (if using Twilio)
- [ ] `TWILIO_PHONE_NUMBER` = (if using Twilio)

### 4. Deploy
- [ ] Click "Deploy" or wait for auto-deploy
- [ ] Wait 2-3 minutes
- [ ] Check deployment logs for errors

### 5. Verify Backend
- [ ] Visit: `https://your-app.railway.app/health`
- [ ] Should return: `{"status": "healthy", "version": "v1"}`
- [ ] Visit: `https://your-app.railway.app/api/v1/docs`
- [ ] Should show API documentation
- [ ] Copy your Railway URL for next step

## 🎨 Vercel Frontend Deployment

### 1. Create Project
- [ ] Go to https://vercel.com
- [ ] Sign in with GitHub
- [ ] Click "Add New Project"
- [ ] Import `1saas-for-all` repository

### 2. Configure Build
- [ ] Framework Preset: `Vite`
- [ ] Root Directory: `frontend`
- [ ] Build Command: `npm run build`
- [ ] Output Directory: `dist`
- [ ] Install Command: `npm install`

### 3. Add Environment Variable
- [ ] Add `VITE_API_URL` = `https://your-app.railway.app/api/v1`
- [ ] (Use the Railway URL from previous step)

### 4. Deploy
- [ ] Click "Deploy"
- [ ] Wait 2-3 minutes
- [ ] Copy your Vercel URL

### 5. Update Backend CORS
- [ ] Go back to Railway
- [ ] Update `CORS_ORIGINS` variable
- [ ] Add your Vercel URL: `https://your-app.vercel.app`
- [ ] Railway will auto-redeploy

## 🗄️ Database Setup

### 1. Run Migrations
- [ ] Go to Supabase Dashboard
- [ ] Open SQL Editor
- [ ] Run migrations in order:
  - [ ] `001_complete_schema_setup.sql`
  - [ ] `002_update_booking_types_location.sql`
  - [ ] `003_update_existing_database.sql`
  - [ ] `004_add_missing_tables.sql`

### 2. Verify Tables
- [ ] Check Table Editor
- [ ] Verify all tables exist:
  - [ ] users
  - [ ] workspaces
  - [ ] contacts
  - [ ] bookings
  - [ ] booking_types
  - [ ] booking_type_availability
  - [ ] analytics_events
  - [ ] (and others)

## ✅ Post-Deployment Testing

### 1. Test Backend
- [ ] Health check: `https://your-app.railway.app/health`
- [ ] API docs: `https://your-app.railway.app/api/v1/docs`
- [ ] Test endpoint: Try GET `/api/v1/public/booking-types/{workspace_id}`

### 2. Test Frontend
- [ ] Visit: `https://your-app.vercel.app`
- [ ] Page loads without errors
- [ ] No CORS errors in console
- [ ] Can navigate between pages

### 3. Test Authentication
- [ ] Register new account
- [ ] Verify email (if configured)
- [ ] Login with credentials
- [ ] Access dashboard
- [ ] Logout

### 4. Test Features
- [ ] Create a contact
- [ ] Create a booking type
- [ ] Set availability
- [ ] View dashboard stats
- [ ] Test public booking page

## 🔧 Troubleshooting

### Backend Issues
- [ ] Check Railway deployment logs
- [ ] Verify all environment variables are set
- [ ] Test database connection
- [ ] Check Supabase credentials

### Frontend Issues
- [ ] Check Vercel deployment logs
- [ ] Verify VITE_API_URL is correct
- [ ] Check browser console for errors
- [ ] Verify CORS is configured

### CORS Errors
- [ ] Backend CORS_ORIGINS includes Vercel URL
- [ ] No trailing slashes in URLs
- [ ] Both http and https if needed
- [ ] Redeploy backend after CORS changes

## 📊 Monitoring

### Set Up Monitoring
- [ ] Enable Vercel Analytics
- [ ] Check Railway metrics
- [ ] Monitor Supabase usage
- [ ] Set up error tracking (Sentry - optional)

### Regular Checks
- [ ] Check deployment logs daily
- [ ] Monitor database usage
- [ ] Check API response times
- [ ] Review error rates

## 🎉 Success Criteria

Your deployment is successful when:
- ✅ Backend health check returns 200
- ✅ Frontend loads without errors
- ✅ Can register and login
- ✅ Can create and view data
- ✅ No CORS errors
- ✅ API documentation accessible
- ✅ Database queries working

## 📝 Notes

**Railway URL**: _______________________________

**Vercel URL**: _______________________________

**Deployment Date**: _______________________________

**Issues Encountered**: 
_______________________________
_______________________________
_______________________________

## 🔗 Quick Links

- Railway Dashboard: https://railway.app/dashboard
- Vercel Dashboard: https://vercel.com/dashboard
- Supabase Dashboard: https://supabase.com/dashboard
- GitHub Repo: https://github.com/utkarshjha1407/1saas-for-all

## 📚 Documentation

- [Railway Setup Guide](./RAILWAY_SETUP.md)
- [Environment Variables Guide](./RAILWAY_ENV_SETUP.md)
- [Quick Deploy Guide](./QUICK_DEPLOY.md)
- [Full Deployment Guide](./DEPLOYMENT_GUIDE.md)
