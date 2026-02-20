# Railway Deployment - Step by Step

## Issue: Railway can't detect the Backend

Railway is looking at the root directory, but our backend is in the `Backend/` folder.

## Solution: Configure Railway Properly

### Option 1: Use Railway Dashboard (Recommended)

1. **Go to Railway Project Settings**
   - Click on your service
   - Go to "Settings" tab

2. **Set Root Directory**
   - Find "Root Directory" setting
   - Set it to: `Backend`
   - Click "Save"

3. **Set Start Command**
   - Find "Start Command" setting
   - Set it to: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
   - Click "Save"

4. **Set Build Command** (Optional)
   - Find "Build Command" setting
   - Set it to: `pip install -r requirements.txt`
   - Click "Save"

5. **Redeploy**
   - Click "Deploy" button
   - Railway will now build from the Backend directory

### Option 2: Use railway.toml (Already Created)

The `railway.toml` file in the root tells Railway how to build:

```toml
[build]
builder = "NIXPACKS"
buildCommand = "cd Backend && pip install -r requirements.txt"

[deploy]
startCommand = "cd Backend && uvicorn app.main:app --host 0.0.0.0 --port $PORT"
```

Just push to GitHub and Railway will use this config.

### Option 3: Create Separate Service

1. **Delete Current Service**
   - Go to Railway dashboard
   - Delete the failed service

2. **Create New Service**
   - Click "New Service"
   - Select "GitHub Repo"
   - Choose your repo

3. **Configure During Creation**
   - Root Directory: `Backend`
   - Start Command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

## Environment Variables

Don't forget to add these in Railway:

```env
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_anon_key
SUPABASE_SERVICE_KEY=your_service_key
SECRET_KEY=your_secret_key
CORS_ORIGINS=https://your-app.vercel.app
ENVIRONMENT=production
DEBUG=False
```

## Verify Deployment

After deployment:

1. Check logs for errors
2. Visit: `https://your-app.railway.app/health`
3. Should return: `{"status": "healthy", "version": "v1"}`
4. Visit: `https://your-app.railway.app/api/v1/docs`
5. Should show API documentation

## Alternative: Use Render Instead

If Railway continues to have issues, try Render:

### Render Setup

1. **Go to Render.com**
   - Sign up with GitHub

2. **New Web Service**
   - Click "New +"
   - Select "Web Service"
   - Connect your repo

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

5. **Create Redis**
   - New → Redis
   - Copy REDIS_URL
   - Add to environment variables

6. **Deploy**
   - Click "Create Web Service"
   - Wait 5-10 minutes

## Troubleshooting

### Railway can't find requirements.txt
- Make sure Root Directory is set to `Backend`
- Check that `Backend/requirements.txt` exists in your repo

### Build fails with Python errors
- Check Python version in `Backend/runtime.txt`
- Verify all dependencies are in `requirements.txt`

### App starts but crashes immediately
- Check environment variables are set
- Look at Railway logs for error messages
- Verify Supabase credentials

### Port binding error
- Make sure start command uses `$PORT` variable
- Railway automatically assigns a port

## Quick Fix Commands

If you need to update the repo:

```bash
# Add railway.toml
git add railway.toml nixpacks.toml
git commit -m "fix: Add Railway configuration files"
git push origin main
```

Railway will automatically redeploy.

## Success Indicators

✅ Build completes without errors
✅ Service shows "Active" status
✅ Health endpoint returns 200
✅ API docs are accessible
✅ No errors in logs

## Next Steps

Once backend is deployed:
1. Copy your Railway URL
2. Update Vercel environment variable: `VITE_API_URL`
3. Redeploy frontend
4. Test the full application
