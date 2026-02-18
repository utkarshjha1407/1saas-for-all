-- Migration: Add staff permissions and workspace activation
-- Step 7: Staff invitations and permissions
-- Step 8: Workspace activation verification

-- Step 1: Add staff permissions table
CREATE TABLE IF NOT EXISTS staff_permissions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    workspace_id UUID NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,
    can_access_inbox BOOLEAN DEFAULT TRUE,
    can_manage_bookings BOOLEAN DEFAULT TRUE,
    can_view_forms BOOLEAN DEFAULT TRUE,
    can_view_inventory BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(user_id, workspace_id)
);

-- Step 2: Add staff invitations table
CREATE TABLE IF NOT EXISTS staff_invitations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    workspace_id UUID NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,
    email VARCHAR(255) NOT NULL,
    invited_by UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    token VARCHAR(255) UNIQUE NOT NULL,
    permissions JSONB NOT NULL DEFAULT '{"can_access_inbox": true, "can_manage_bookings": true, "can_view_forms": true, "can_view_inventory": true}',
    status VARCHAR(50) NOT NULL CHECK (status IN ('pending', 'accepted', 'expired')) DEFAULT 'pending',
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
    accepted_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Step 3: Add workspace activation fields
ALTER TABLE workspaces
ADD COLUMN IF NOT EXISTS is_activated BOOLEAN DEFAULT FALSE,
ADD COLUMN IF NOT EXISTS activated_at TIMESTAMP WITH TIME ZONE,
ADD COLUMN IF NOT EXISTS activation_checklist JSONB DEFAULT '{
    "communication_connected": false,
    "booking_type_exists": false,
    "availability_defined": false
}';

-- Step 4: Create indexes
CREATE INDEX IF NOT EXISTS idx_staff_permissions_user ON staff_permissions(user_id);
CREATE INDEX IF NOT EXISTS idx_staff_permissions_workspace ON staff_permissions(workspace_id);
CREATE INDEX IF NOT EXISTS idx_staff_invitations_workspace ON staff_invitations(workspace_id);
CREATE INDEX IF NOT EXISTS idx_staff_invitations_email ON staff_invitations(email);
CREATE INDEX IF NOT EXISTS idx_staff_invitations_token ON staff_invitations(token);
CREATE INDEX IF NOT EXISTS idx_workspaces_activated ON workspaces(is_activated);

-- Step 5: Create function to check activation requirements
CREATE OR REPLACE FUNCTION check_workspace_activation_requirements(p_workspace_id UUID)
RETURNS JSONB AS $$
DECLARE
    v_checklist JSONB;
    v_has_integration BOOLEAN;
    v_has_booking_type BOOLEAN;
    v_has_availability BOOLEAN;
BEGIN
    -- Check if communication channel is connected
    SELECT EXISTS(
        SELECT 1 FROM integrations 
        WHERE workspace_id = p_workspace_id 
        AND is_active = TRUE
    ) INTO v_has_integration;
    
    -- Check if at least one booking type exists
    SELECT EXISTS(
        SELECT 1 FROM booking_types 
        WHERE workspace_id = p_workspace_id
    ) INTO v_has_booking_type;
    
    -- Check if availability is defined (at least one availability slot)
    SELECT EXISTS(
        SELECT 1 FROM availability_slots 
        WHERE workspace_id = p_workspace_id
    ) INTO v_has_availability;
    
    -- Build checklist
    v_checklist := jsonb_build_object(
        'communication_connected', v_has_integration,
        'booking_type_exists', v_has_booking_type,
        'availability_defined', v_has_availability,
        'all_requirements_met', v_has_integration AND v_has_booking_type AND v_has_availability
    );
    
    RETURN v_checklist;
END;
$$ LANGUAGE plpgsql;

-- Verification
SELECT 'Migration 006 completed successfully' AS status;
