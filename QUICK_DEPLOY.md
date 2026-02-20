# Quick Deploy Guide

## 🚀 Deploy in 15 Minutes

### Step 1: Deploy Frontend to Vercel (5 min)

1. Go to https://vercel.com and sign in with GitHub
2. Click "Add New Project"
3. Import `1saas-for-all` repository
4. Configure:
   - Framework: Vite
   - Root Directory: `frontend`
   - Build Command: `npm run build`
   - Output Directory: `dist`
5. Add environment variable:
   - `VITE_API_URL` = `https://your-backend-url.railway.app/api/v1` (we'll update this)
6. Click "Deploy"
7. Copy your Vercel URL: `https://your-app.vercel.app`

### Step 2: Deploy Backend to Railway (10 min)

1. Go to https://railway.app and sign in with GitHub
2. Click "New Project" → "Deploy from GitHub repo"
3. Select `1saas-for-all`
4. Click "Add variables" and add:
   ```
   SUPABASE_URL=your_supabase_url
   SUPABASE_KEY=your_supabase_anon_key
   SUPABASE_SERVICE_KEY=your_service_key
   SECRET_KEY=generate_a_random_secret_key
   CORS_ORIGINS=https://your-app.vercel.app
   ENVIRONMENT=production
   ```
5. Click "New Service" → "Redis" (for background tasks)
6. In Settings:
   - Root Directory: `Backend`
   - Start Command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
7. Click "Deploy"
8. Copy your Railway URL: `https://your-app.railway.app`

### Step 3: Update Frontend Environment

1. Go back to Vercel project settings
2. Update `VITE_API_URL` to your Railway URL
3. Redeploy frontend

### Step 4: Test Your Deployment

1. Visit your Vercel URL
2. Register a new account
3. Create a booking type
4. Test the public booking page

## ✅ Done!

Your app is now live:
- Frontend: https://your-app.vercel.app
- Backend: https://your-app.railway.app
- API Docs: https://your-app.railway.app/api/v1/docs

## 🔧 Alternative: Use Render for Backend

If you prefer Render over Railway:

1. Go to https://render.com
2. New → Web Service
3. Connect GitHub repo
4. Configure:
   - Name: careops-backend
   - Root Directory: Backend
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
5. Add same environment variables
6. Create Redis instance separately

## 💡 Pro Tips

1. **Generate Secret Key**:
   ```python
   import secrets
   print(secrets.token_urlsafe(32))
   ```

2. **Test Locally First**:
   ```bash
   # Update frontend/.env
   VITE_API_URL=https://your-backend.railway.app/api/v1
   
   # Test
   cd frontend && npm run dev
   ```

3. **Monitor Deployments**:
   - Vercel: Check deployment logs
   - Railway: Check service logs
   - Supabase: Check database activity

4. **Custom Domain** (Optional):
   - Vercel: Settings → Domains → Add
   - Railway: Settings → Networking → Custom Domain

## 🆘 Common Issues

**Frontend can't connect to backend**:
- Check CORS_ORIGINS includes your Vercel URL
- Verify VITE_API_URL is correct
- Check browser console for errors

**Backend won't start**:
- Check all environment variables are set
- Verify Python version in runtime.txt
- Check Railway/Render logs

**Database errors**:
- Run all migrations in Supabase
- Verify Supabase credentials
- Check RLS policies are enabled

## 📊 Free Tier Limits

- Vercel: 100GB bandwidth/month
- Railway: $5 credit/month (~500 hours)
- Supabase: 500MB database

Should be enough for development and testing!
