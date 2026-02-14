"""Automation tasks for CareOps"""
from datetime import datetime, timedelta
import structlog
from app.tasks.celery_app import celery_app
from app.db.supabase_client import get_supabase_client
from app.services.communication.email_provider import EmailService
from app.services.communication.sms_provider import SMSService
from app.models.enums import FormStatus, AlertType, AlertPriority

logger = structlog.get_logger()


@celery_app.task(name="app.tasks.automation_tasks.send_welcome_message")
def send_welcome_message(contact_id: str, workspace_id: str):
    """Send welcome message to new contact"""
    try:
        supabase = get_supabase_client().service_client
        
        # Get contact details
        contact = supabase.table("contacts").select("*").eq("id", contact_id).execute()
        if not contact.data:
            return
        
        contact_data = contact.data[0]
        
        # Get workspace details
        workspace = supabase.table("workspaces").select("*").eq("id", workspace_id).execute()
        workspace_data = workspace.data[0]
        
        # Send welcome email
        if contact_data.get("email"):
            email_service = EmailService()
            email_service.send_email(
                to=contact_data["email"],
                subject=f"Welcome to {workspace_data['name']}",
                content=f"<p>Thank you for contacting us! We'll get back to you shortly.</p>"
            )
        
        logger.info("welcome_message_sent", contact_id=contact_id)
    except Exception as e:
        logger.exception("welcome_message_failed", contact_id=contact_id, error=str(e))


@celery_app.task(name="app.tasks.automation_tasks.send_booking_confirmation")
def send_booking_confirmation(booking_id: str):
    """Send booking confirmation"""
    try:
        supabase = get_supabase_client().service_client
        
        # Get booking with related data
        booking = supabase.table("bookings").select("*, contacts(*), booking_types(*), workspaces(*)").eq("id", booking_id).execute()
        if not booking.data:
            return
        
        booking_data = booking.data[0]
        contact = booking_data["contacts"]
        booking_type = booking_data["booking_types"]
        workspace = booking_data["workspaces"]
        
        # Send confirmation email
        if contact.get("email"):
            email_service = EmailService()
            scheduled_time = datetime.fromisoformat(booking_data["scheduled_at"])
            
            email_service.send_email(
                to=contact["email"],
                subject=f"Booking Confirmed - {booking_type['name']}",
                content=f"""
                <h2>Your booking is confirmed!</h2>
                <p><strong>Service:</strong> {booking_type['name']}</p>
                <p><strong>Date & Time:</strong> {scheduled_time.strftime('%B %d, %Y at %I:%M %p')}</p>
                <p><strong>Duration:</strong> {booking_type['duration_minutes']} minutes</p>
                <p><strong>Location:</strong> {booking_type.get('location', workspace['address'])}</p>
                """
            )
        
        logger.info("booking_confirmation_sent", booking_id=booking_id)
    except Exception as e:
        logger.exception("booking_confirmation_failed", booking_id=booking_id, error=str(e))


@celery_app.task(name="app.tasks.automation_tasks.send_booking_reminders")
def send_booking_reminders():
    """Send reminders for upcoming bookings"""
    try:
        supabase = get_supabase_client().service_client
        
        # Get bookings in next 24 hours
        tomorrow = datetime.now() + timedelta(hours=24)
        now = datetime.now()
        
        bookings = supabase.table("bookings").select("*, contacts(*), booking_types(*), workspaces(*)").gte("scheduled_at", now.isoformat()).lte("scheduled_at", tomorrow.isoformat()).eq("status", "confirmed").execute()
        
        for booking in bookings.data:
            contact = booking["contacts"]
            booking_type = booking["booking_types"]
            scheduled_time = datetime.fromisoformat(booking["scheduled_at"])
            
            # Send reminder via email
            if contact.get("email"):
                email_service = EmailService()
                email_service.send_email(
                    to=contact["email"],
                    subject=f"Reminder: {booking_type['name']} Tomorrow",
                    content=f"""
                    <h2>Reminder: Your appointment is tomorrow</h2>
                    <p><strong>Service:</strong> {booking_type['name']}</p>
                    <p><strong>Date & Time:</strong> {scheduled_time.strftime('%B %d, %Y at %I:%M %p')}</p>
                    """
                )
            
            # Send SMS reminder if phone available
            if contact.get("phone"):
                sms_service = SMSService()
                sms_service.send_sms(
                    to=contact["phone"],
                    content=f"Reminder: {booking_type['name']} tomorrow at {scheduled_time.strftime('%I:%M %p')}"
                )
        
        logger.info("booking_reminders_sent", count=len(bookings.data))
    except Exception as e:
        logger.exception("booking_reminders_failed", error=str(e))


@celery_app.task(name="app.tasks.automation_tasks.send_form_after_booking")
def send_form_after_booking(booking_id: str):
    """Send forms after booking creation"""
    try:
        supabase = get_supabase_client().service_client
        
        # Get booking
        booking = supabase.table("bookings").select("*, contacts(*), booking_types(*)").eq("id", booking_id).execute()
        if not booking.data:
            return
        
        booking_data = booking.data[0]
        
        # Get forms for this booking type
        forms = supabase.table("form_templates").select("*").contains("booking_type_ids", [booking_data["booking_type_id"]]).execute()
        
        for form in forms.data:
            # Create form submission
            supabase.table("form_submissions").insert({
                "form_template_id": form["id"],
                "booking_id": booking_id,
                "contact_id": booking_data["contact_id"],
                "workspace_id": booking_data["workspace_id"],
                "status": FormStatus.PENDING.value,
                "data": {}
            }).execute()
        
        logger.info("forms_sent_after_booking", booking_id=booking_id, form_count=len(forms.data))
    except Exception as e:
        logger.exception("send_forms_failed", booking_id=booking_id, error=str(e))


@celery_app.task(name="app.tasks.automation_tasks.check_overdue_forms")
def check_overdue_forms():
    """Check for overdue forms and create alerts"""
    try:
        supabase = get_supabase_client().service_client
        
        # Get pending forms older than 48 hours
        cutoff = datetime.now() - timedelta(hours=48)
        
        forms = supabase.table("form_submissions").select("*").eq("status", FormStatus.PENDING.value).lt("created_at", cutoff.isoformat()).execute()
        
        for form in forms.data:
            # Update status to overdue
            supabase.table("form_submissions").update({"status": FormStatus.OVERDUE.value}).eq("id", form["id"]).execute()
            
            # Create alert
            supabase.table("alerts").insert({
                "workspace_id": form["workspace_id"],
                "alert_type": AlertType.OVERDUE_FORM.value,
                "priority": AlertPriority.MEDIUM.value,
                "title": "Form Overdue",
                "message": f"Form submission {form['id']} is overdue",
                "metadata": {"form_id": form["id"], "booking_id": form["booking_id"]}
            }).execute()
        
        logger.info("overdue_forms_checked", count=len(forms.data))
    except Exception as e:
        logger.exception("check_overdue_forms_failed", error=str(e))


@celery_app.task(name="app.tasks.automation_tasks.check_inventory_levels")
def check_inventory_levels():
    """Check inventory levels and create alerts"""
    try:
        supabase = get_supabase_client().service_client
        
        # Get low stock items
        items = supabase.table("inventory_items").select("*").eq("is_low_stock", True).execute()
        
        for item in items.data:
            priority = AlertPriority.CRITICAL.value if item["quantity"] == 0 else AlertPriority.HIGH.value
            alert_type = AlertType.CRITICAL_INVENTORY.value if item["quantity"] == 0 else AlertType.LOW_INVENTORY.value
            
            # Check if alert already exists
            existing = supabase.table("alerts").select("id").eq("workspace_id", item["workspace_id"]).eq("alert_type", alert_type).contains("metadata", {"item_id": item["id"]}).eq("is_resolved", False).execute()
            
            if not existing.data:
                supabase.table("alerts").insert({
                    "workspace_id": item["workspace_id"],
                    "alert_type": alert_type,
                    "priority": priority,
                    "title": f"{'Out of Stock' if item['quantity'] == 0 else 'Low Stock'}: {item['name']}",
                    "message": f"{item['name']} has {item['quantity']} {item['unit']} remaining",
                    "metadata": {"item_id": item["id"], "quantity": item["quantity"]}
                }).execute()
        
        logger.info("inventory_levels_checked", low_stock_count=len(items.data))
    except Exception as e:
        logger.exception("check_inventory_failed", error=str(e))
