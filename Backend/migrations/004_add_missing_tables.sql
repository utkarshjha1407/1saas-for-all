-- Migration: Add Missing Tables
-- This adds booking_type_availability and analytics_events tables

-- Create booking_type_availability table if it doesn't exist
CREATE TABLE IF NOT EXISTS public.booking_type_availability (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    booking_type_id UUID NOT NULL REFERENCES public.booking_types(id) ON DELETE CASCADE,
    day_of_week INTEGER NOT NULL CHECK (day_of_week >= 0 AND day_of_week <= 6),
    start_time TIME NOT NULL,
    end_time TIME NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    CONSTRAINT valid_time_range CHECK (end_time > start_time)
);

-- Create index for faster lookups
CREATE INDEX IF NOT EXISTS idx_booking_type_availability_booking_type 
ON public.booking_type_availability(booking_type_id);

CREATE INDEX IF NOT EXISTS idx_booking_type_availability_day 
ON public.booking_type_availability(day_of_week);

-- Create analytics_events table if it doesn't exist
CREATE TABLE IF NOT EXISTS public.analytics_events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workspace_id UUID NOT NULL REFERENCES public.workspaces(id) ON DELETE CASCADE,
    event_type VARCHAR(100) NOT NULL,
    event_data JSONB,
    ip_address VARCHAR(45),
    user_agent TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for analytics
CREATE INDEX IF NOT EXISTS idx_analytics_events_workspace 
ON public.analytics_events(workspace_id);

CREATE INDEX IF NOT EXISTS idx_analytics_events_type 
ON public.analytics_events(event_type);

CREATE INDEX IF NOT EXISTS idx_analytics_events_created 
ON public.analytics_events(created_at DESC);

-- Enable RLS on new tables
ALTER TABLE public.booking_type_availability ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.analytics_events ENABLE ROW LEVEL SECURITY;

-- RLS Policies for booking_type_availability
CREATE POLICY "Users can view availability for their workspace booking types"
ON public.booking_type_availability FOR SELECT
USING (
    EXISTS (
        SELECT 1 FROM public.booking_types bt
        JOIN public.users u ON u.workspace_id = bt.workspace_id
        WHERE bt.id = booking_type_availability.booking_type_id
        AND u.id = auth.uid()
    )
);

CREATE POLICY "Owners can manage availability for their workspace"
ON public.booking_type_availability FOR ALL
USING (
    EXISTS (
        SELECT 1 FROM public.booking_types bt
        JOIN public.users u ON u.workspace_id = bt.workspace_id
        WHERE bt.id = booking_type_availability.booking_type_id
        AND u.id = auth.uid()
        AND u.role = 'owner'
    )
);

-- RLS Policies for analytics_events
CREATE POLICY "Users can view analytics for their workspace"
ON public.analytics_events FOR SELECT
USING (
    EXISTS (
        SELECT 1 FROM public.users
        WHERE users.workspace_id = analytics_events.workspace_id
        AND users.id = auth.uid()
    )
);

CREATE POLICY "System can insert analytics events"
ON public.analytics_events FOR INSERT
WITH CHECK (true);

-- Add updated_at trigger for booking_type_availability
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_booking_type_availability_updated_at
    BEFORE UPDATE ON public.booking_type_availability
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Grant permissions
GRANT ALL ON public.booking_type_availability TO authenticated;
GRANT ALL ON public.analytics_events TO authenticated;
GRANT SELECT ON public.booking_type_availability TO anon;
GRANT INSERT ON public.analytics_events TO anon;

COMMENT ON TABLE public.booking_type_availability IS 'Stores availability schedules for booking types';
COMMENT ON TABLE public.analytics_events IS 'Tracks analytics events for workspaces';
