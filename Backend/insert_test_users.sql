-- ============================================
-- CAREOPS TEST USERS - Quick Insert
-- Run this in Supabase SQL Editor
-- Password for all users: password123
-- ============================================

-- Note: Password hash for "password123" 
-- You'll need to generate this using bcrypt with your backend
-- For now, use the Python seeding script instead

-- This is a reference of what the seeding script creates:

/*
WORKSPACE 1: Wellness Clinic
- Owner: alice@wellnessclinic.com / password123
- Staff: bob@wellnessclinic.com / password123  
- Staff: carol@wellnessclinic.com / password123

WORKSPACE 2: Therapy Center
- Owner: david@therapycenter.com / password123
- Staff: emma@therapycenter.com / password123

To create these users, run:
cd Backend
venv\Scripts\activate
python seed_test_data.py
*/

-- Check if users exist
SELECT email, full_name, role, workspace_id 
FROM users 
WHERE email LIKE '%@wellnessclinic.com' 
   OR email LIKE '%@therapycenter.com'
ORDER BY email;

-- Check workspaces
SELECT id, name, slug, status, onboarding_step
FROM workspaces
WHERE slug IN ('wellness-clinic', 'therapy-center');
