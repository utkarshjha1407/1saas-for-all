-- Migration: Update form_templates for file upload support
-- This migration changes form_templates from custom form builder to file upload

-- Step 1: Drop the old fields column and add file-related columns
ALTER TABLE form_templates 
DROP COLUMN IF EXISTS fields,
ADD COLUMN IF NOT EXISTS file_url TEXT,
ADD COLUMN IF NOT EXISTS file_type VARCHAR(50),
ADD COLUMN IF NOT EXISTS file_size INTEGER;

-- Step 2: Make file_url NOT NULL for new records (existing records might be null)
-- Note: If you have existing data, you may need to populate file_url first

-- Step 3: Update form_submissions to track viewing/download
ALTER TABLE form_submissions
ADD COLUMN IF NOT EXISTS viewed_at TIMESTAMP WITH TIME ZONE,
ADD COLUMN IF NOT EXISTS downloaded_at TIMESTAMP WITH TIME ZONE;

-- Step 4: Add index for faster queries
CREATE INDEX IF NOT EXISTS idx_form_templates_workspace ON form_templates(workspace_id);
CREATE INDEX IF NOT EXISTS idx_form_submissions_status ON form_submissions(status);
CREATE INDEX IF NOT EXISTS idx_form_submissions_booking ON form_submissions(booking_id);

-- Verification
SELECT 'Migration 004 completed successfully' AS status;
