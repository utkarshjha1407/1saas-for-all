"""Dashboard endpoints"""
from fastapi import APIRouter, Depends
from datetime import datetime
from supabase import Client

from app.db.supabase_client import get_supabase_service
from app.schemas.dashboard import DashboardStats, BookingOverview, LeadOverview, FormOverview, InventoryOverview
from app.schemas.auth import TokenData
from app.core.security import require_staff_or_owner
from app.services.booking_service import BookingService

router = APIRouter()


@router.get("/stats", response_model=DashboardStats)
async def get_dashboard_stats(
    current_user: TokenData = Depends(require_staff_or_owner),
    supabase: Client = Depends(get_supabase_service)
):
    """Get dashboard statistics"""
    workspace_id = current_user.workspace_id
    
    if not workspace_id:
        # Return empty stats if no workspace
        from app.schemas.dashboard import BookingOverview, LeadOverview, FormOverview, InventoryOverview
        return DashboardStats(
            bookings=BookingOverview(today_count=0, upcoming_count=0, completed_count=0, no_show_count=0),
            leads=LeadOverview(new_inquiries=0, ongoing_conversations=0, unanswered_messages=0),
            forms=FormOverview(pending_count=0, overdue_count=0, completed_count=0),
            inventory=InventoryOverview(low_stock_items=0, critical_items=0),
            total_alerts=0,
            critical_alerts=0,
            generated_at=datetime.now()
        )
    
    # Booking stats
    booking_service = BookingService(supabase)
    today_bookings = await booking_service.get_today_bookings(workspace_id)
    upcoming_bookings = await booking_service.get_upcoming_bookings(workspace_id)
    
    completed_count = len([b for b in today_bookings if b["status"] == "completed"])
    no_show_count = len([b for b in today_bookings if b["status"] == "no_show"])
    
    # Lead stats
    conversations = supabase.table("conversations").select("*").eq("workspace_id", workspace_id).execute()
    unanswered = len([c for c in conversations.data if c["unread_count"] > 0])
    
    # Form stats
    forms = supabase.table("form_submissions").select("status").eq("workspace_id", workspace_id).execute()
    pending_forms = len([f for f in forms.data if f["status"] == "pending"])
    overdue_forms = len([f for f in forms.data if f["status"] == "overdue"])
    completed_forms = len([f for f in forms.data if f["status"] == "completed"])
    
    # Inventory stats
    inventory = supabase.table("inventory_items").select("*").eq("workspace_id", workspace_id).execute()
    low_stock = len([i for i in inventory.data if i["is_low_stock"]])
    critical = len([i for i in inventory.data if i["quantity"] == 0])
    
    # Alert stats
    alerts = supabase.table("alerts").select("*").eq("workspace_id", workspace_id).eq("is_resolved", False).execute()
    total_alerts = len(alerts.data)
    critical_alerts = len([a for a in alerts.data if a["priority"] == "critical"])
    
    return DashboardStats(
        bookings=BookingOverview(
            today_count=len(today_bookings),
            upcoming_count=len(upcoming_bookings),
            completed_count=completed_count,
            no_show_count=no_show_count
        ),
        leads=LeadOverview(
            new_inquiries=len(conversations.data),
            ongoing_conversations=len([c for c in conversations.data if not c["is_automated_paused"]]),
            unanswered_messages=unanswered
        ),
        forms=FormOverview(
            pending_count=pending_forms,
            overdue_count=overdue_forms,
            completed_count=completed_forms
        ),
        inventory=InventoryOverview(
            low_stock_items=low_stock,
            critical_items=critical
        ),
        total_alerts=total_alerts,
        critical_alerts=critical_alerts,
        generated_at=datetime.now()
    )
