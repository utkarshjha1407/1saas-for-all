-- ============================================
-- CAREOPS ENHANCED DATABASE SCHEMA
-- Hackathon Alignment + Enhanced Features
-- ============================================

-- ============================================
-- PHASE 1: ALTER EXISTING TABLES
-- ============================================

-- Add workspace slug and branding
ALTER TABLE workspaces ADD COLUMN IF NOT EXISTS slug VARCHAR(100) UNIQUE;
ALTER TABLE workspaces ADD COLUMN IF NOT EXISTS logo_url TEXT;
ALTER TABLE workspaces ADD COLUMN IF NOT EXISTS primary_color VARCHAR(7) DEFAULT '#3b82f6';
ALTER TABLE workspaces ADD COLUMN IF NOT EXISTS secondary_color VARCHAR(7) DEFAULT '#8b5cf6';
ALTER TABLE workspaces ADD COLUMN IF NOT EXISTS is_onboarding_complete BOOLEAN DEFAULT FALSE;

-- Add automation pause tracking to conversations
ALTER TABLE conversations ADD COLUMN IF NOT EXISTS automation_paused_at TIMESTAMP WITH TIME ZONE;
ALTER TABLE conversations ADD COLUMN IF NOT EXISTS automation_paused_by UUID REFERENCES users(id);

-- Add form submission access tokens
ALTER TABLE form_submissions ADD COLUMN IF NOT EXISTS access_token VARCHAR(255) UNIQUE;
ALTER TABLE form_submissions ADD COLUMN IF NOT EXISTS public_url TEXT;

-- Add contact source tracking
ALTER TABLE contacts ADD COLUMN IF NOT EXISTS source VARCHAR(50) DEFAULT 'manual';
ALTER TABLE contacts ADD COLUMN IF NOT EXISTS source_url TEXT;

-- Add booking public reference
ALTER TABLE bookings ADD COLUMN IF NOT EXISTS public_reference VARCHAR(50) UNIQUE;

-- Create indexes for new columns
CREATE INDEX IF NOT EXISTS idx_workspaces_slug ON workspaces(slug);
CREATE INDEX IF NOT EXISTS idx_form_submissions_token ON form_submissions(access_token);
CREATE INDEX IF NOT EXISTS idx_bookings_reference ON bookings(public_reference);

-- ============================================
-- PHASE 2: NEW TABLES
-- ============================================

-- Public forms configuration
CREATE TABLE IF NOT EXISTS public_forms (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    workspace_id UUID NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    fields JSONB NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    submit_button_text VARCHAR(100) DEFAULT 'Submit',
    success_message TEXT DEFAULT 'Thank you! We''ll be in touch soon.',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Analytics events tracking
CREATE TABLE IF NOT EXISTS analytics_events (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    workspace_id UUID NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,
    event_type VARCHAR(100) NOT NULL,
    event_data JSONB,
    user_agent TEXT,
    ip_address VARCHAR(45),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Payment tracking
CREATE TABLE IF NOT EXISTS payments (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    workspace_id UUID NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,
    booking_id UUID NOT NULL REFERENCES bookings(id) ON DELETE CASCADE,
    amount DECIMAL(10, 2) NOT NULL,
    currency VARCHAR(3) DEFAULT 'USD',
    status VARCHAR(50) NOT NULL CHECK (status IN ('pending', 'completed', 'failed', 'refunded')),
    payment_method VARCHAR(50),
    stripe_payment_id VARCHAR(255),
    stripe_customer_id VARCHAR(255),
    metadata JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Automation rules (custom automation builder)
CREATE TABLE IF NOT EXISTS automation_rules (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    workspace_id UUID NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    trigger_type VARCHAR(100) NOT NULL,
    trigger_config JSONB NOT NULL,
    actions JSONB NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    execution_count INTEGER DEFAULT 0,
    last_executed_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Automation execution log
CREATE TABLE IF NOT EXISTS automation_executions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    automation_rule_id UUID NOT NULL REFERENCES automation_rules(id) ON DELETE CASCADE,
    workspace_id UUID NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,
    trigger_data JSONB,
    status VARCHAR(50) NOT NULL CHECK (status IN ('success', 'failed', 'skipped')),
    error_message TEXT,
    executed_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Message templates
CREATE TABLE IF NOT EXISTS message_templates (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    workspace_id UUID NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    subject VARCHAR(255),
    content TEXT NOT NULL,
    channel VARCHAR(50) NOT NULL CHECK (channel IN ('email', 'sms', 'both')),
    variables JSONB,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Staff assignments
CREATE TABLE IF NOT EXISTS staff_assignments (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    workspace_id UUID NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,
    staff_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    resource_type VARCHAR(50) NOT NULL CHECK (resource_type IN ('booking', 'conversation', 'contact')),
    resource_id UUID NOT NULL,
    assigned_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    assigned_by UUID REFERENCES users(id)
);

-- Workspace invitations
CREATE TABLE IF NOT EXISTS workspace_invitations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    workspace_id UUID NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,
    email VARCHAR(255) NOT NULL,
    role VARCHAR(50) NOT NULL CHECK (role IN ('owner', 'staff')),
    token VARCHAR(255) UNIQUE NOT NULL,
    invited_by UUID NOT NULL REFERENCES users(id),
    status VARCHAR(50) NOT NULL DEFAULT 'pending' CHECK (status IN ('pending', 'accepted', 'expired')),
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Calendar integrations
CREATE TABLE IF NOT EXISTS calendar_integrations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    workspace_id UUID NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    provider VARCHAR(50) NOT NULL CHECK (provider IN ('google', 'outlook', 'ical')),
    calendar_id VARCHAR(255) NOT NULL,
    access_token TEXT,
    refresh_token TEXT,
    sync_enabled BOOLEAN DEFAULT TRUE,
    last_sync_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Notification preferences
CREATE TABLE IF NOT EXISTS notification_preferences (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    notification_type VARCHAR(100) NOT NULL,
    channel VARCHAR(50) NOT NULL CHECK (channel IN ('email', 'sms', 'push', 'in_app')),
    is_enabled BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(user_id, notification_type, channel)
);

-- Audit log
CREATE TABLE IF NOT EXISTS audit_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    workspace_id UUID NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,
    user_id UUID REFERENCES users(id) ON DELETE SET NULL,
    action VARCHAR(100) NOT NULL,
    resource_type VARCHAR(50) NOT NULL,
    resource_id UUID,
    changes JSONB,
    ip_address VARCHAR(45),
    user_agent TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ============================================
-- PHASE 3: INDEXES FOR PERFORMANCE
-- ============================================

CREATE INDEX IF NOT EXISTS idx_public_forms_workspace ON public_forms(workspace_id);
CREATE INDEX IF NOT EXISTS idx_analytics_workspace ON analytics_events(workspace_id);
CREATE INDEX IF NOT EXISTS idx_analytics_type ON analytics_events(event_type);
CREATE INDEX IF NOT EXISTS idx_analytics_created ON analytics_events(created_at);
CREATE INDEX IF NOT EXISTS idx_payments_workspace ON payments(workspace_id);
CREATE INDEX IF NOT EXISTS idx_payments_booking ON payments(booking_id);
CREATE INDEX IF NOT EXISTS idx_payments_status ON payments(status);
CREATE INDEX IF NOT EXISTS idx_automation_rules_workspace ON automation_rules(workspace_id);
CREATE INDEX IF NOT EXISTS idx_automation_rules_active ON automation_rules(is_active);
CREATE INDEX IF NOT EXISTS idx_automation_executions_rule ON automation_executions(automation_rule_id);
CREATE INDEX IF NOT EXISTS idx_message_templates_workspace ON message_templates(workspace_id);
CREATE INDEX IF NOT EXISTS idx_staff_assignments_workspace ON staff_assignments(workspace_id);
CREATE INDEX IF NOT EXISTS idx_staff_assignments_staff ON staff_assignments(staff_id);
CREATE INDEX IF NOT EXISTS idx_staff_assignments_resource ON staff_assignments(resource_type, resource_id);
CREATE INDEX IF NOT EXISTS idx_invitations_workspace ON workspace_invitations(workspace_id);
CREATE INDEX IF NOT EXISTS idx_invitations_token ON workspace_invitations(token);
CREATE INDEX IF NOT EXISTS idx_invitations_status ON workspace_invitations(status);
CREATE INDEX IF NOT EXISTS idx_calendar_integrations_workspace ON calendar_integrations(workspace_id);
CREATE INDEX IF NOT EXISTS idx_calendar_integrations_user ON calendar_integrations(user_id);
CREATE INDEX IF NOT EXISTS idx_notification_prefs_user ON notification_preferences(user_id);
CREATE INDEX IF NOT EXISTS idx_audit_logs_workspace ON audit_logs(workspace_id);
CREATE INDEX IF NOT EXISTS idx_audit_logs_user ON audit_logs(user_id);
CREATE INDEX IF NOT EXISTS idx_audit_logs_created ON audit_logs(created_at);

-- ============================================
-- PHASE 4: TRIGGERS
-- ============================================

-- Apply updated_at triggers to new tables
CREATE TRIGGER update_public_forms_updated_at 
    BEFORE UPDATE ON public_forms 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_payments_updated_at 
    BEFORE UPDATE ON payments 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_automation_rules_updated_at 
    BEFORE UPDATE ON automation_rules 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_message_templates_updated_at 
    BEFORE UPDATE ON message_templates 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_calendar_integrations_updated_at 
    BEFORE UPDATE ON calendar_integrations 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Trigger to generate form submission access token
CREATE OR REPLACE FUNCTION generate_form_submission_token()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.access_token IS NULL THEN
        NEW.access_token := encode(gen_random_bytes(32), 'hex');
        NEW.public_url := '/public/form/' || NEW.id || '/' || NEW.access_token;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER set_form_submission_token
    BEFORE INSERT ON form_submissions
    FOR EACH ROW EXECUTE FUNCTION generate_form_submission_token();

-- Trigger to generate booking public reference
CREATE OR REPLACE FUNCTION generate_booking_reference()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.public_reference IS NULL THEN
        NEW.public_reference := 'BK-' || UPPER(SUBSTRING(MD5(RANDOM()::TEXT) FROM 1 FOR 8));
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER set_booking_reference
    BEFORE INSERT ON bookings
    FOR EACH ROW EXECUTE FUNCTION generate_booking_reference();

-- Trigger to update inventory low stock status
CREATE OR REPLACE FUNCTION update_inventory_low_stock()
RETURNS TRIGGER AS $$
BEGIN
    NEW.is_low_stock := NEW.quantity <= NEW.low_stock_threshold;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER check_inventory_low_stock
    BEFORE INSERT OR UPDATE OF quantity, low_stock_threshold ON inventory_items
    FOR EACH ROW EXECUTE FUNCTION update_inventory_low_stock();

-- ============================================
-- PHASE 5: ROW LEVEL SECURITY
-- ============================================

ALTER TABLE public_forms ENABLE ROW LEVEL SECURITY;
ALTER TABLE analytics_events ENABLE ROW LEVEL SECURITY;
ALTER TABLE payments ENABLE ROW LEVEL SECURITY;
ALTER TABLE automation_rules ENABLE ROW LEVEL SECURITY;
ALTER TABLE automation_executions ENABLE ROW LEVEL SECURITY;
ALTER TABLE message_templates ENABLE ROW LEVEL SECURITY;
ALTER TABLE staff_assignments ENABLE ROW LEVEL SECURITY;
ALTER TABLE workspace_invitations ENABLE ROW LEVEL SECURITY;
ALTER TABLE calendar_integrations ENABLE ROW LEVEL SECURITY;
ALTER TABLE notification_preferences ENABLE ROW LEVEL SECURITY;
ALTER TABLE audit_logs ENABLE ROW LEVEL SECURITY;

-- ============================================
-- PHASE 6: HELPER FUNCTIONS
-- ============================================

-- Function to check if workspace is ready for activation
CREATE OR REPLACE FUNCTION check_workspace_activation_ready(p_workspace_id UUID)
RETURNS JSONB AS $$
DECLARE
    result JSONB;
    has_integration BOOLEAN;
    has_booking_type BOOLEAN;
    has_availability BOOLEAN;
    has_public_form BOOLEAN;
    missing_items TEXT[];
BEGIN
    -- Check for at least one active integration
    SELECT EXISTS(
        SELECT 1 FROM integrations 
        WHERE workspace_id = p_workspace_id 
        AND status = 'active'
    ) INTO has_integration;
    
    -- Check for at least one booking type
    SELECT EXISTS(
        SELECT 1 FROM booking_types 
        WHERE workspace_id = p_workspace_id 
        AND is_active = TRUE
    ) INTO has_booking_type;
    
    -- Check for availability slots
    SELECT EXISTS(
        SELECT 1 FROM availability_slots 
        WHERE workspace_id = p_workspace_id
    ) INTO has_availability;
    
    -- Check for public form
    SELECT EXISTS(
        SELECT 1 FROM public_forms 
        WHERE workspace_id = p_workspace_id 
        AND is_active = TRUE
    ) INTO has_public_form;
    
    -- Build missing items array
    missing_items := ARRAY[]::TEXT[];
    IF NOT has_integration THEN
        missing_items := array_append(missing_items, 'Active email or SMS integration');
    END IF;
    IF NOT has_booking_type THEN
        missing_items := array_append(missing_items, 'At least one booking type');
    END IF;
    IF NOT has_availability THEN
        missing_items := array_append(missing_items, 'Availability slots defined');
    END IF;
    IF NOT has_public_form THEN
        missing_items := array_append(missing_items, 'Public contact form');
    END IF;
    
    -- Build result
    result := jsonb_build_object(
        'is_ready', (has_integration AND has_booking_type AND has_availability AND has_public_form),
        'has_integration', has_integration,
        'has_booking_type', has_booking_type,
        'has_availability', has_availability,
        'has_public_form', has_public_form,
        'missing_items', missing_items
    );
    
    RETURN result;
END;
$$ LANGUAGE plpgsql;

-- Function to get today's dashboard stats
CREATE OR REPLACE FUNCTION get_today_dashboard_stats(p_workspace_id UUID)
RETURNS JSONB AS $$
DECLARE
    result JSONB;
    today_start TIMESTAMP WITH TIME ZONE;
    today_end TIMESTAMP WITH TIME ZONE;
BEGIN
    today_start := DATE_TRUNC('day', NOW());
    today_end := today_start + INTERVAL '1 day';
    
    SELECT jsonb_build_object(
        'todays_bookings', (
            SELECT COUNT(*) FROM bookings 
            WHERE workspace_id = p_workspace_id 
            AND scheduled_at >= today_start 
            AND scheduled_at < today_end
        ),
        'new_inquiries_24h', (
            SELECT COUNT(*) FROM contacts 
            WHERE workspace_id = p_workspace_id 
            AND created_at >= NOW() - INTERVAL '24 hours'
        ),
        'unread_messages', (
            SELECT COALESCE(SUM(unread_count), 0) FROM conversations 
            WHERE workspace_id = p_workspace_id
        ),
        'overdue_forms', (
            SELECT COUNT(*) FROM form_submissions 
            WHERE workspace_id = p_workspace_id 
            AND status = 'overdue'
        ),
        'critical_inventory', (
            SELECT COUNT(*) FROM inventory_items 
            WHERE workspace_id = p_workspace_id 
            AND quantity = 0
        ),
        'pending_bookings', (
            SELECT COUNT(*) FROM bookings 
            WHERE workspace_id = p_workspace_id 
            AND status = 'pending'
        )
    ) INTO result;
    
    RETURN result;
END;
$$ LANGUAGE plpgsql;

-- ============================================
-- PHASE 7: SEED DATA FOR TESTING
-- ============================================

-- Insert default message templates (will be created during onboarding)
-- These are examples and should be customized per workspace

COMMENT ON TABLE public_forms IS 'Public contact forms that customers can fill without logging in';
COMMENT ON TABLE analytics_events IS 'Tracks all public page visits and interactions for analytics';
COMMENT ON TABLE payments IS 'Payment tracking for bookings with Stripe integration';
COMMENT ON TABLE automation_rules IS 'Custom automation rules created by workspace owners';
COMMENT ON TABLE automation_executions IS 'Log of all automation rule executions';
COMMENT ON TABLE message_templates IS 'Reusable message templates for email and SMS';
COMMENT ON TABLE staff_assignments IS 'Assigns staff members to specific bookings or conversations';
COMMENT ON TABLE workspace_invitations IS 'Pending invitations for new staff members';
COMMENT ON TABLE calendar_integrations IS 'Google/Outlook calendar sync configurations';
COMMENT ON TABLE notification_preferences IS 'User notification preferences per channel';
COMMENT ON TABLE audit_logs IS 'Complete audit trail of all system actions';

-- ============================================
-- MIGRATION COMPLETE
-- ============================================
-- Run this script on your Supabase database to add all enhanced features
-- Make sure to backup your database before running!
