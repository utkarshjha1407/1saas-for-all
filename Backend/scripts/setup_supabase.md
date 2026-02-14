# Supabase Setup Guide

## Step 1: Create Supabase Project

1. Go to [supabase.com](https://supabase.com)
2. Sign in or create an account
3. Click "New Project"
4. Fill in:
   - Project name: `careops`
   - Database password: (save this securely)
   - Region: Choose closest to your users
5. Wait for project to be created (~2 minutes)

## Step 2: Run Database Schema

1. In your Supabase dashboard, go to "SQL Editor"
2. Click "New Query"
3. Copy the entire contents of `supabase_schema.sql`
4. Paste into the SQL editor
5. Click "Run" or press Ctrl+Enter
6. Verify all tables were created (check "Table Editor" tab)

## Step 3: Get API Credentials

1. Go to Settings > API
2. Copy these values to your `.env` file:
   - **Project URL**: `SUPABASE_URL`
   - **anon public key**: `SUPABASE_KEY`
   - **service_role key**: `SUPABASE_SERVICE_KEY` (⚠️ Keep secret!)

## Step 4: Configure Row Level Security (Optional)

For production, configure RLS policies:

```sql
-- Example: Allow users to access their workspace data
CREATE POLICY workspace_access ON workspaces
FOR ALL
USING (
    auth.uid() = owner_id 
    OR auth.uid() IN (
        SELECT id FROM users WHERE workspace_id = workspaces.id
    )
);

-- Add similar policies for other tables
```

## Step 5: Enable Realtime (Optional)

For real-time features:

1. Go to Database > Replication
2. Enable replication for tables:
   - `messages`
   - `bookings`
   - `alerts`
   - `conversations`

## Step 6: Set Up Storage (Optional)

For file uploads (forms, documents):

1. Go to Storage
2. Create bucket: `form-uploads`
3. Set policies for authenticated access

## Step 7: Configure Email Templates (Optional)

1. Go to Authentication > Email Templates
2. Customize confirmation and reset emails
3. Add your branding

## Verification

Test your setup:

```bash
# In your backend directory
python -c "from app.db.supabase_client import get_supabase_client; print('✓ Supabase connected')"
```

## Troubleshooting

### Connection Issues
- Verify URL and keys are correct
- Check if project is paused (free tier)
- Ensure no firewall blocking

### Schema Errors
- Run schema in order (dependencies matter)
- Check for existing tables (drop if needed)
- Verify UUID extension is enabled

### RLS Issues
- Service role key bypasses RLS
- Test policies with anon key
- Check auth.uid() is set correctly

## Next Steps

1. Test API endpoints
2. Create first user via `/api/v1/auth/register`
3. Create workspace
4. Configure integrations
