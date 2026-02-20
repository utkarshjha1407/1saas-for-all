# Vercel Frontend Deployment - Step by Step

## ✅ Fixed: vercel.json Configuration

The build configuration has been fixed. Vercel will now build correctly.

## 🚀 Deploy to Vercel

### Step 1: Go to Vercel

1. Visit: https://vercel.com
2. Click "Sign Up" or "Login"
3. Choose "Continue with GitHub"
4. Authorize Vercel to access your GitHub

### Step 2: Import Project

1. Click "Add New..." → "Project"
2. Find your repository: `1saas-for-all`
3. Click "Import"

### Step 3: Configure Project

**IMPORTANT: Set these settings correctly**

1. **Framework Preset**: Select `Vite`
2. **Root Directory**: Click "Edit" and set to `frontend`
3. **Build Command**: Leave as default or set to `npm run build`
4. **Output Directory**: Leave as default or set to `dist`
5. **Install Command**: Leave as default or set to `npm install`

### Step 4: Add Environment Variable

1. Expand "Environment Variables" section
2. Add variable:
   - **Key**: `VITE_API_URL`
   - **Value**: `http://localhost:8000/api/v1` (temporary - we'll update after backend deployment)
3. Click "Add"

### Step 5: Deploy

1. Click "Deploy" button
2. Wait 2-3 minutes for build to complete
3. You'll see "Congratulations!" when done

### Step 6: Get Your URL

1. Copy your Vercel URL (e.g., `https://your-app.vercel.app`)
2. Click "Visit" to see your deployed app

## 📝 Configuration Summary

Your Vercel project should have these settings:

```
Framework: Vite
Root Directory: frontend
Build Command: npm run build
Output Directory: dist
Install Command: npm install

Environment Variables:
VITE_API_URL = http://localhost:8000/api/v1 (update after backend deployment)
```

## 🔄 Update After Backend Deployment

Once your Railway backend is deployed:

1. Go to Vercel project → Settings → Environment Variables
2. Edit `VITE_API_URL`
3. Change to: `https://your-app.railway.app/api/v1`
4. Go to Deployments tab
5. Click "..." on latest deployment → "Redeploy"

## ✅ Verify Deployment

After deployment:

1. **Visit your Vercel URL**
   - Should load the login/register page
   - No build errors

2. **Check Browser Console**
   - Press F12
   - Go to Console tab
   - Should see no errors (API errors are OK for now)

3. **Test Navigation**
   - Click around the app
   - Pages should load
   - UI should be responsive

## 🐛 Troubleshooting

### Build Failed: "cd frontend: No such file or directory"

**Solution**: Make sure Root Directory is set to `frontend` in Vercel settings

1. Go to Project Settings
2. Find "Root Directory"
3. Set to: `frontend`
4. Save and redeploy

### Build Failed: "npm: command not found"

**Solution**: Vercel should auto-detect Node.js. If not:

1. Go to Project Settings → General
2. Check Node.js Version
3. Should be 18.x or higher

### Build Succeeds but App Shows Blank Page

**Solution**: Check output directory

1. Go to Project Settings → Build & Development Settings
2. Output Directory should be: `dist`
3. Save and redeploy

### API Calls Failing (CORS Errors)

**Solution**: This is expected until backend is deployed

1. Deploy backend to Railway first
2. Update `VITE_API_URL` with Railway URL
3. Update backend CORS to include Vercel URL
4. Redeploy both

### Environment Variable Not Working

**Solution**: Redeploy after adding variables

1. Environment variables only apply to new deployments
2. After adding/changing variables, redeploy
3. Go to Deployments → Click "..." → "Redeploy"

## 📊 Vercel Dashboard Overview

After deployment, you'll see:

- **Deployments**: List of all deployments
- **Analytics**: Traffic and performance data
- **Settings**: Project configuration
- **Domains**: Custom domain setup

## 🔗 Custom Domain (Optional)

To add a custom domain:

1. Go to Project Settings → Domains
2. Click "Add"
3. Enter your domain (e.g., `app.yourdomain.com`)
4. Follow DNS configuration instructions
5. Wait for DNS propagation (5-30 minutes)

## 💰 Vercel Pricing

**Free Tier Includes:**
- Unlimited deployments
- 100GB bandwidth/month
- Automatic HTTPS
- Global CDN
- Preview deployments

**Pro Tier ($20/month):**
- 1TB bandwidth
- Advanced analytics
- Team collaboration
- Priority support

## 🎯 Success Checklist

- [ ] Vercel account created
- [ ] Project imported from GitHub
- [ ] Root Directory set to `frontend`
- [ ] Framework set to Vite
- [ ] Environment variable added
- [ ] Deployment successful
- [ ] App loads in browser
- [ ] No build errors
- [ ] URL copied for backend CORS

## 📚 Next Steps

1. ✅ Frontend deployed to Vercel
2. → Deploy backend to Railway
3. → Update VITE_API_URL with Railway URL
4. → Update backend CORS with Vercel URL
5. → Test full application

## 🆘 Need Help?

- Vercel Docs: https://vercel.com/docs
- Vite Docs: https://vitejs.dev/guide/
- Check deployment logs in Vercel dashboard
- Look for errors in browser console

## 📞 Support

If deployment fails:
1. Check the build logs in Vercel
2. Verify all settings match this guide
3. Make sure `frontend/` directory exists in your repo
4. Ensure `package.json` is in `frontend/` directory
