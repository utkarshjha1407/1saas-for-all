-- Migration: Update inventory_items to link with booking types
-- This enables automatic inventory tracking per booking

-- Step 1: Add booking type linking and usage tracking
ALTER TABLE inventory_items 
ADD COLUMN IF NOT EXISTS booking_type_ids UUID[] DEFAULT '{}',
ADD COLUMN IF NOT EXISTS quantity_per_booking INTEGER DEFAULT 1;

-- Step 2: Add index for faster queries
CREATE INDEX IF NOT EXISTS idx_inventory_items_workspace ON inventory_items(workspace_id);
CREATE INDEX IF NOT EXISTS idx_inventory_items_low_stock ON inventory_items(workspace_id, is_low_stock) WHERE is_low_stock = TRUE;
CREATE INDEX IF NOT EXISTS idx_inventory_usage_item ON inventory_usage(inventory_item_id);
CREATE INDEX IF NOT EXISTS idx_inventory_usage_booking ON inventory_usage(booking_id);

-- Step 3: Create function to update is_low_stock automatically
CREATE OR REPLACE FUNCTION update_inventory_low_stock()
RETURNS TRIGGER AS $$
BEGIN
    NEW.is_low_stock := NEW.quantity <= NEW.low_stock_threshold;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Step 4: Create trigger to auto-update is_low_stock
DROP TRIGGER IF EXISTS trigger_update_inventory_low_stock ON inventory_items;
CREATE TRIGGER trigger_update_inventory_low_stock
    BEFORE INSERT OR UPDATE OF quantity, low_stock_threshold
    ON inventory_items
    FOR EACH ROW
    EXECUTE FUNCTION update_inventory_low_stock();

-- Verification
SELECT 'Migration 005 completed successfully' AS status;
