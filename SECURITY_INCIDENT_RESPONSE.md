# 🚨 SECURITY INCIDENT RESPONSE

## What Happened
GitHub detected exposed API keys in your public repository.

## Exposed Keys
- ✅ SUPABASE_KEY (anon key) - Safe to expose, no action needed
- ⚠️ SUPABASE_SERVICE_KEY - **MUST ROTATE**
- ⚠️ RESEND_API_KEY - **MUST ROTATE**
- ⚠️ SECRET_KEY - **MUST ROTATE**

## Immediate Actions (DO NOW)

### 1. Rotate Resend API Key
**Exposed Key**: `re_b5jsbV2A_GavHqX5fR4r44JgnwaJ9eaow`

Steps:
1. Go to https://resend.com/api-keys
2. Find and DELETE the exposed key
3. Click "Create API Key"
4. Copy the new key
5. Update `Backend/.env`: `RESEND_API_KEY=<new_key>`

### 2. Rotate Supabase Service Role Key
**Project**: https://supabase.com/dashboard/project/mriwhoavwsncxsozgmeb

Steps:
1. Go to Settings → API
2. Find "service_role" key (secret)
3. Click "Reset" or "Regenerate"
4. Copy the new key
5. Update `Backend/.env`: `SUPABASE_SERVICE_KEY=<new_key>`

**Note**: The anon key is safe to expose publicly (it's meant for frontend use)

### 3. Generate New SECRET_KEY
**Exposed Key**: `D7-bS7e_5hcJZWYZM7VwNGOGqzgUnaGmEAleFlPBUks`

New key generated: `hvEUpFm4KYtSXAUT2oKWTLdYphtp0zhv7BCvixS2UbM`

Update `Backend/.env`:
```
SECRET_KEY=hvEUpFm4KYtSXAUT2oKWTLdYphtp0zhv7BCvixS2UbM
```

### 4. Update Railway Environment Variables
After rotating keys locally, update Railway:
1. Go to Railway dashboard
2. Click on your service
3. Go to Variables tab
4. Update:
   - `RESEND_API_KEY` = <new_resend_key>
   - `SUPABASE_SERVICE_KEY` = <new_supabase_service_key>
   - `SECRET_KEY` = hvEUpFm4KYtSXAUT2oKWTLdYphtp0zhv7BCvixS2UbM
5. Click "Redeploy"

### 5. Verify .env is Gitignored
✅ Already verified - `Backend/.env` is in `.gitignore`

### 6. Check for Exposed Keys in Git History
Run this command to search for any keys in git history:
```bash
git log -p | grep -i "re_b5jsbV2A"
```

If found, you'll need to use `git filter-branch` or BFG Repo-Cleaner to remove them.

## Prevention Checklist

- [x] `.env` files in `.gitignore`
- [x] `.env.example` files have placeholder values only
- [ ] All exposed keys rotated
- [ ] Railway environment variables updated
- [ ] Local `.env` files updated with new keys
- [ ] Test application with new keys
- [ ] Enable GitHub secret scanning alerts (already enabled)
- [ ] Consider using a secrets manager (AWS Secrets Manager, HashiCorp Vault)

## Testing After Key Rotation

1. **Test Locally**:
   ```bash
   cd Backend
   uvicorn app.main:app --reload
   ```
   - Visit http://localhost:8000/health
   - Test authentication endpoints
   - Test email sending (if using Resend)

2. **Test Railway**:
   - Wait for redeploy
   - Visit https://your-app.railway.app/health
   - Test API endpoints

## Additional Security Measures

1. **Enable 2FA** on all services:
   - GitHub
   - Supabase
   - Resend
   - Railway

2. **Use Environment-Specific Keys**:
   - Development keys for local
   - Production keys for Railway/Vercel
   - Never mix them

3. **Regular Key Rotation**:
   - Rotate production keys every 90 days
   - Rotate immediately if exposed

4. **Monitor Access Logs**:
   - Check Supabase logs for suspicious activity
   - Check Resend usage for unexpected emails
   - Monitor Railway logs

## What Keys Are Safe to Expose?

✅ **Safe (Public)**:
- Supabase anon key (designed for frontend)
- Supabase URL
- API endpoints

⚠️ **Never Expose (Secret)**:
- Supabase service_role key
- JWT SECRET_KEY
- Email API keys (Resend, SendGrid)
- SMS API keys (Twilio)
- Database passwords
- Redis passwords

## If You See Suspicious Activity

1. **Immediately**:
   - Rotate ALL keys
   - Check Supabase logs for unauthorized access
   - Check Resend for unauthorized emails sent
   - Change passwords on all services

2. **Review**:
   - Database for unauthorized changes
   - User accounts for suspicious activity
   - Email logs for spam

3. **Report**:
   - Contact Supabase support if database compromised
   - Contact Resend support if email quota exceeded
   - File incident report with your organization

## Status

- [ ] Resend API key rotated
- [ ] Supabase service key rotated
- [ ] SECRET_KEY updated
- [ ] Railway variables updated
- [ ] Local .env updated
- [ ] Application tested
- [ ] Deployment verified

## Timeline

- **Detection**: GitHub secret scanning alert received
- **Response Started**: Immediately
- **Keys Rotated**: [Pending - do now]
- **Services Updated**: [Pending - after rotation]
- **Verification**: [Pending - after update]

## Contact

If you need help:
- Supabase Support: https://supabase.com/dashboard/support
- Resend Support: https://resend.com/support
- Railway Support: https://railway.app/help
