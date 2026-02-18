-- Migration: Update booking_types table to use location_type instead of location
-- Date: 2026-02-15

-- Rename location column to location_type and add constraint
ALTER TABLE booking_types 
RENAME COLUMN location TO location_type;

-- Add NOT NULL constraint with default value
ALTER TABLE booking_types 
ALTER COLUMN location_type SET DEFAULT 'video';

-- Update any NULL values to 'video'
UPDATE booking_types 
SET location_type = 'video' 
WHERE location_type IS NULL;

-- Add check constraint for valid location types
ALTER TABLE booking_types
ADD CONSTRAINT check_location_type 
CHECK (location_type IN ('in-person', 'phone', 'video', 'client-location'));
