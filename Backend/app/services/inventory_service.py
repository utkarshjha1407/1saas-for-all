"""Inventory service"""
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from supabase import Client
import structlog

logger = structlog.get_logger()


class InventoryService:
    """Service for managing inventory items and usage"""
    
    def __init__(self, supabase: Client):
        self.supabase = supabase
    
    async def create_item(self, item_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create inventory item"""
        try:
            # Calculate is_low_stock
            item_data['is_low_stock'] = item_data['quantity'] <= item_data['low_stock_threshold']
            
            response = self.supabase.table("inventory_items").insert(item_data).execute()
            
            if not response.data:
                raise Exception("Failed to create inventory item")
            
            logger.info("inventory_item_created", item_id=response.data[0]["id"])
            return response.data[0]
            
        except Exception as e:
            logger.error("create_inventory_item_failed", error=str(e))
            raise
    
    async def get_items(self, workspace_id: str, low_stock_only: bool = False) -> List[Dict[str, Any]]:
        """Get inventory items for workspace"""
        try:
            query = self.supabase.table("inventory_items").select("*").eq("workspace_id", workspace_id)
            
            if low_stock_only:
                query = query.eq("is_low_stock", True)
            
            response = query.order("name").execute()
            return response.data or []
            
        except Exception as e:
            logger.error("get_inventory_items_failed", error=str(e))
            raise
    
    async def get_item(self, item_id: str) -> Optional[Dict[str, Any]]:
        """Get single inventory item"""
        try:
            response = self.supabase.table("inventory_items").select("*").eq("id", item_id).single().execute()
            return response.data
            
        except Exception as e:
            logger.error("get_inventory_item_failed", item_id=item_id, error=str(e))
            return None
    
    async def update_item(self, item_id: str, update_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update inventory item"""
        try:
            # Recalculate is_low_stock if quantity or threshold changed
            if 'quantity' in update_data or 'low_stock_threshold' in update_data:
                item = await self.get_item(item_id)
                if item:
                    quantity = update_data.get('quantity', item['quantity'])
                    threshold = update_data.get('low_stock_threshold', item['low_stock_threshold'])
                    update_data['is_low_stock'] = quantity <= threshold
            
            response = self.supabase.table("inventory_items").update(update_data).eq("id", item_id).execute()
            
            if not response.data:
                raise Exception("Failed to update inventory item")
            
            logger.info("inventory_item_updated", item_id=item_id)
            return response.data[0]
            
        except Exception as e:
            logger.error("update_inventory_item_failed", item_id=item_id, error=str(e))
            raise
    
    async def delete_item(self, item_id: str) -> None:
        """Delete inventory item"""
        try:
            self.supabase.table("inventory_items").delete().eq("id", item_id).execute()
            logger.info("inventory_item_deleted", item_id=item_id)
            
        except Exception as e:
            logger.error("delete_inventory_item_failed", item_id=item_id, error=str(e))
            raise
    
    async def adjust_quantity(self, item_id: str, adjustment: int, reason: Optional[str] = None) -> Dict[str, Any]:
        """Adjust inventory quantity (positive to add, negative to subtract)"""
        try:
            item = await self.get_item(item_id)
            if not item:
                raise Exception("Item not found")
            
            new_quantity = max(0, item['quantity'] + adjustment)
            
            update_data = {
                'quantity': new_quantity,
                'is_low_stock': new_quantity <= item['low_stock_threshold']
            }
            
            response = self.supabase.table("inventory_items").update(update_data).eq("id", item_id).execute()
            
            logger.info("inventory_adjusted", 
                       item_id=item_id, 
                       adjustment=adjustment, 
                       new_quantity=new_quantity,
                       reason=reason)
            
            return response.data[0]
            
        except Exception as e:
            logger.error("adjust_inventory_failed", item_id=item_id, error=str(e))
            raise
    
    async def record_usage(self, usage_data: Dict[str, Any]) -> Dict[str, Any]:
        """Record inventory usage for a booking"""
        try:
            # Create usage record
            response = self.supabase.table("inventory_usage").insert(usage_data).execute()
            
            if not response.data:
                raise Exception("Failed to record usage")
            
            # Deduct from inventory
            await self.adjust_quantity(
                usage_data['inventory_item_id'],
                -usage_data['quantity_used'],
                f"Used for booking {usage_data['booking_id']}"
            )
            
            logger.info("inventory_usage_recorded", 
                       item_id=usage_data['inventory_item_id'],
                       booking_id=usage_data['booking_id'],
                       quantity=usage_data['quantity_used'])
            
            return response.data[0]
            
        except Exception as e:
            logger.error("record_usage_failed", error=str(e))
            raise
    
    async def get_usage_history(self, item_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Get usage history for an item"""
        try:
            response = (
                self.supabase.table("inventory_usage")
                .select("*, bookings(scheduled_at, booking_types(name))")
                .eq("inventory_item_id", item_id)
                .order("created_at", desc=True)
                .limit(limit)
                .execute()
            )
            
            return response.data or []
            
        except Exception as e:
            logger.error("get_usage_history_failed", item_id=item_id, error=str(e))
            raise
    
    async def get_forecast(self, workspace_id: str, days_ahead: int = 30) -> List[Dict[str, Any]]:
        """Get inventory usage forecast"""
        try:
            # Get all items
            items = await self.get_items(workspace_id)
            
            # Get upcoming bookings
            start_date = datetime.now()
            end_date = start_date + timedelta(days=days_ahead)
            
            bookings_response = (
                self.supabase.table("bookings")
                .select("booking_type_id")
                .eq("workspace_id", workspace_id)
                .gte("scheduled_at", start_date.isoformat())
                .lte("scheduled_at", end_date.isoformat())
                .execute()
            )
            
            bookings = bookings_response.data or []
            
            # Calculate forecast for each item
            forecasts = []
            for item in items:
                booking_type_ids = item.get('booking_type_ids', [])
                
                # Count upcoming bookings that use this item
                upcoming_bookings = sum(
                    1 for b in bookings 
                    if b['booking_type_id'] in booking_type_ids
                )
                
                quantity_per_booking = item.get('quantity_per_booking', 1)
                estimated_usage = upcoming_bookings * quantity_per_booking
                
                # Calculate days until depleted
                days_until_depleted = None
                if estimated_usage > 0 and item['quantity'] > 0:
                    days_until_depleted = int((item['quantity'] / estimated_usage) * days_ahead)
                
                # Recommend reorder if will run out before forecast period ends
                reorder_recommended = (
                    item['is_low_stock'] or 
                    (days_until_depleted is not None and days_until_depleted < days_ahead)
                )
                
                forecasts.append({
                    'item_id': item['id'],
                    'item_name': item['name'],
                    'current_quantity': item['quantity'],
                    'low_stock_threshold': item['low_stock_threshold'],
                    'quantity_per_booking': quantity_per_booking,
                    'upcoming_bookings': upcoming_bookings,
                    'estimated_usage': estimated_usage,
                    'days_until_depleted': days_until_depleted,
                    'reorder_recommended': reorder_recommended
                })
            
            return forecasts
            
        except Exception as e:
            logger.error("get_forecast_failed", error=str(e))
            raise
    
    async def process_booking_inventory(self, booking_id: str, booking_type_id: str, workspace_id: str) -> None:
        """Automatically deduct inventory for a booking"""
        try:
            # Get items linked to this booking type
            items_response = (
                self.supabase.table("inventory_items")
                .select("*")
                .eq("workspace_id", workspace_id)
                .execute()
            )
            
            items = items_response.data or []
            
            # Filter items that are linked to this booking type
            linked_items = [
                item for item in items 
                if booking_type_id in (item.get('booking_type_ids') or [])
            ]
            
            # Record usage for each linked item
            for item in linked_items:
                quantity_used = item.get('quantity_per_booking', 1)
                
                await self.record_usage({
                    'inventory_item_id': item['id'],
                    'booking_id': booking_id,
                    'quantity_used': quantity_used,
                    'notes': f"Automatic deduction for booking"
                })
            
            logger.info("booking_inventory_processed", 
                       booking_id=booking_id,
                       items_count=len(linked_items))
            
        except Exception as e:
            logger.error("process_booking_inventory_failed", 
                        booking_id=booking_id, 
                        error=str(e))
            # Don't raise - inventory tracking shouldn't block booking creation
