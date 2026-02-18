-- Verification Script: Check if database is properly migrated
-- Run this in Supabase SQL Editor to verify your schema

-- Check if all required tables exist
SELECT 
    'Tables Check' as check_type,
    CASE 
        WHEN COUNT(*) = 13 THEN '✓ PASS'
        ELSE '✗ FAIL - Missing tables'
    END as status,
    COUNT(*) as found,
    13 as expected
FROM information_schema.tables 
WHERE table_schema = 'public' 
AND table_name IN (
    'users', 'workspaces', 'contacts', 'booking_types', 'availability_slots',
    'bookings', 'conversations', 'messages', 'form_templates', 'form_submissions',
    'inventory_items', 'inventory_usage', 'alerts', 'integrations'
);

-- Check booking_types has location_type column (not location)
SELECT 
    'Booking Types Column' as check_type,
    CASE 
        WHEN EXISTS (
            SELECT 1 FROM information_schema.columns 
            WHERE table_name = 'booking_types' AND column_name = 'location_type'
        ) THEN '✓ PASS - location_type exists'
        WHEN EXISTS (
            SELECT 1 FROM information_schema.columns 
            WHERE table_name = 'booking_types' AND column_name = 'location'
        ) THEN '✗ FAIL - Still using old "location" column. Run migration!'
        ELSE '✗ FAIL - booking_types table missing'
    END as status;

-- Check location_type constraint
SELECT 
    'Location Type Constraint' as check_type,
    CASE 
        WHEN EXISTS (
            SELECT 1 FROM information_schema.table_constraints 
            WHERE constraint_name = 'check_location_type' AND table_name = 'booking_types'
        ) THEN '✓ PASS'
        ELSE '✗ FAIL - Missing check constraint'
    END as status;

-- Check availability_slots table structure
SELECT 
    'Availability Slots Table' as check_type,
    CASE 
        WHEN COUNT(*) >= 6 THEN '✓ PASS'
        ELSE '✗ FAIL - Missing columns'
    END as status,
    COUNT(*) as columns_found
FROM information_schema.columns 
WHERE table_name = 'availability_slots';

-- Check form_templates table structure
SELECT 
    'Form Templates Table' as check_type,
    CASE 
        WHEN COUNT(*) >= 6 THEN '✓ PASS'
        ELSE '✗ FAIL - Missing columns'
    END as status,
    COUNT(*) as columns_found
FROM information_schema.columns 
WHERE table_name = 'form_templates';

-- Check form_submissions table structure
SELECT 
    'Form Submissions Table' as check_type,
    CASE 
        WHEN COUNT(*) >= 8 THEN '✓ PASS'
        ELSE '✗ FAIL - Missing columns'
    END as status,
    COUNT(*) as columns_found
FROM information_schema.columns 
WHERE table_name = 'form_submissions';

-- Check indexes
SELECT 
    'Indexes Check' as check_type,
    CASE 
        WHEN COUNT(*) >= 15 THEN '✓ PASS'
        ELSE '⚠ WARNING - Some indexes missing (not critical)'
    END as status,
    COUNT(*) as indexes_found
FROM pg_indexes 
WHERE schemaname = 'public' 
AND indexname LIKE 'idx_%';

-- List all tables with row counts
SELECT 
    table_name,
    (SELECT COUNT(*) FROM information_schema.columns WHERE columns.table_name = tables.table_name) as column_count,
    pg_size_pretty(pg_total_relation_size(quote_ident(table_name)::regclass)) as size
FROM information_schema.tables 
WHERE table_schema = 'public' 
AND table_type = 'BASE TABLE'
ORDER BY table_name;

-- Summary
SELECT 
    '=== MIGRATION STATUS ===' as summary,
    CASE 
        WHEN (
            SELECT COUNT(*) FROM information_schema.columns 
            WHERE table_name = 'booking_types' AND column_name = 'location_type'
        ) > 0 
        AND (
            SELECT COUNT(*) FROM information_schema.tables 
            WHERE table_name IN ('availability_slots', 'form_templates', 'form_submissions')
        ) = 3
        THEN '✓ DATABASE IS UP TO DATE'
        ELSE '✗ MIGRATION NEEDED - Run Backend/migrations/003_update_existing_database.sql'
    END as status;
