-- Migration 003: Update Existing Database for Steps 4 & 5
-- Run this if you already have a database and need to update it
-- This is safe to run multiple times (idempotent)

-- Step 1: Update booking_types table to use location_type
DO $$ 
BEGIN
    -- Check if location column exists and location_type doesn't
    IF EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'booking_types' AND column_name = 'location'
    ) AND NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'booking_types' AND column_name = 'location_type'
    ) THEN
        -- Rename location to location_type
        ALTER TABLE booking_types RENAME COLUMN location TO location_type;
        
        -- Set default value
        ALTER TABLE booking_types ALTER COLUMN location_type SET DEFAULT 'video';
        
        -- Update any NULL values
        UPDATE booking_types SET location_type = 'video' WHERE location_type IS NULL;
        
        RAISE NOTICE 'Renamed location to location_type in booking_types table';
    END IF;
    
    -- Add check constraint if it doesn't exist
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.table_constraints 
        WHERE constraint_name = 'check_location_type' AND table_name = 'booking_types'
    ) THEN
        ALTER TABLE booking_types
        ADD CONSTRAINT check_location_type 
        CHECK (location_type IN ('in-person', 'phone', 'video', 'client-location'));
        
        RAISE NOTICE 'Added check constraint for location_type';
    END IF;
END $$;

-- Step 2: Ensure availability_slots table exists
CREATE TABLE IF NOT EXISTS availability_slots (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    workspace_id UUID NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,
    booking_type_id UUID NOT NULL REFERENCES booking_types(id) ON DELETE CASCADE,
    day_of_week INTEGER NOT NULL CHECK (day_of_week BETWEEN 0 AND 6),
    start_time TIME NOT NULL,
    end_time TIME NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Step 3: Ensure form_templates table exists
CREATE TABLE IF NOT EXISTS form_templates (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    workspace_id UUID NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    fields JSONB NOT NULL,
    booking_type_ids UUID[],
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Step 4: Ensure form_submissions table exists
CREATE TABLE IF NOT EXISTS form_submissions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    form_template_id UUID NOT NULL REFERENCES form_templates(id) ON DELETE CASCADE,
    booking_id UUID NOT NULL REFERENCES bookings(id) ON DELETE CASCADE,
    contact_id UUID NOT NULL REFERENCES contacts(id) ON DELETE CASCADE,
    workspace_id UUID NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,
    status VARCHAR(50) NOT NULL CHECK (status IN ('pending', 'in_progress', 'completed', 'overdue')),
    data JSONB NOT NULL,
    submitted_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Step 5: Create missing indexes
CREATE INDEX IF NOT EXISTS idx_booking_types_workspace ON booking_types(workspace_id);
CREATE INDEX IF NOT EXISTS idx_availability_booking_type ON availability_slots(booking_type_id);
CREATE INDEX IF NOT EXISTS idx_availability_workspace ON availability_slots(workspace_id);
CREATE INDEX IF NOT EXISTS idx_form_templates_workspace ON form_templates(workspace_id);
CREATE INDEX IF NOT EXISTS idx_form_submissions_workspace ON form_submissions(workspace_id);
CREATE INDEX IF NOT EXISTS idx_form_submissions_status ON form_submissions(status);
CREATE INDEX IF NOT EXISTS idx_form_submissions_booking ON form_submissions(booking_id);

-- Step 6: Add comments for documentation
COMMENT ON TABLE booking_types IS 'Service/meeting types with duration and location (Step 4)';
COMMENT ON COLUMN booking_types.location_type IS 'Type of location: in-person, phone, video, or client-location';
COMMENT ON COLUMN booking_types.duration_minutes IS 'Duration in minutes: 15, 30, 45, 60, 90, or 120';

COMMENT ON TABLE availability_slots IS 'Weekly availability schedule for booking types (Step 4)';
COMMENT ON COLUMN availability_slots.day_of_week IS 'Day of week: 0=Sunday, 1=Monday, ..., 6=Saturday';

COMMENT ON TABLE form_templates IS 'Custom form templates linked to booking types (Step 5)';
COMMENT ON COLUMN form_templates.fields IS 'JSONB array of form field definitions';
COMMENT ON COLUMN form_templates.booking_type_ids IS 'Array of booking type UUIDs this form is linked to';

COMMENT ON TABLE form_submissions IS 'Form submission tracking for bookings (Step 5)';
COMMENT ON COLUMN form_submissions.status IS 'Status: pending, in_progress, completed, or overdue';
COMMENT ON COLUMN form_submissions.data IS 'JSONB object containing submitted form data';

-- Step 7: Verify data integrity
DO $$ 
DECLARE
    booking_types_count INTEGER;
    availability_count INTEGER;
    form_templates_count INTEGER;
BEGIN
    SELECT COUNT(*) INTO booking_types_count FROM booking_types;
    SELECT COUNT(*) INTO availability_count FROM availability_slots;
    SELECT COUNT(*) INTO form_templates_count FROM form_templates;
    
    RAISE NOTICE 'Migration complete!';
    RAISE NOTICE 'Booking types: %', booking_types_count;
    RAISE NOTICE 'Availability slots: %', availability_count;
    RAISE NOTICE 'Form templates: %', form_templates_count;
END $$;
