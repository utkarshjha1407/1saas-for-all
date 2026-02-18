"""Public endpoints (no authentication required)"""
from fastapi import APIRouter, Depends, HTTPException, status, Request
from supabase import Client
from typing import List, Dict, Any
from datetime import datetime, timedelta
import structlog
from collections import defaultdict
from time import time

from app.db.supabase_client import get_supabase
from app.schemas.workspace import WorkspacePublicResponse
from app.schemas.contact import ContactCreate, ContactResponse
from app.schemas.booking import (
    BookingCreate, 
    BookingResponse, 
    BookingTypeResponse,
    PublicBookingCreate
)
from app.services.booking_type_service import BookingTypeService
from app.schemas.form import FormSubmissionPublicCreate, FormSubmissionResponse
from app.services.workspace_service import WorkspaceService
from app.services.booking_service import BookingService
from app.tasks.automation_tasks import (
    send_welcome_message,
    send_booking_confirmation,
    send_form_after_booking,
)

router = APIRouter()
logger = structlog.get_logger()

# Simple in-memory rate limiting (for production, use Redis)
rate_limit_store = defaultdict(list)
RATE_LIMIT_REQUESTS = 10
RATE_LIMIT_WINDOW = 60  # seconds


def check_rate_limit(request: Request) -> None:
    """Check if request exceeds rate limit"""
    client_ip = request.client.host if request.client else "unknown"
    current_time = time()
    
    # Clean old entries
    rate_limit_store[client_ip] = [
        timestamp for timestamp in rate_limit_store[client_ip]
        if current_time - timestamp < RATE_LIMIT_WINDOW
    ]
    
    # Check rate limit
    if len(rate_limit_store[client_ip]) >= RATE_LIMIT_REQUESTS:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many requests. Please try again later."
        )
    
    # Add current request
    rate_limit_store[client_ip].append(current_time)


@router.get("/booking-types/{workspace_id}", response_model=List[BookingTypeResponse])
async def get_public_booking_types(
    workspace_id: str,
    request: Request,
    supabase: Client = Depends(get_supabase)
):
    """Get available booking types for workspace (public endpoint)"""
    # Apply rate limiting
    check_rate_limit(request)
    
    try:
        # Verify workspace exists
        workspace_response = (
            supabase.table("workspaces")
            .select("id")
            .eq("id", workspace_id)
            .single()
            .execute()
        )
        
        if not workspace_response.data:
            logger.warning("workspace_not_found", workspace_id=workspace_id)
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Workspace not found"
            )
        
        # Get active booking types
        service = BookingTypeService(supabase)
        booking_types = await service.get_booking_types(workspace_id, active_only=True)
        
        logger.info("public_booking_types_fetched", workspace_id=workspace_id, count=len(booking_types))
        return booking_types
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("get_public_booking_types_failed", workspace_id=workspace_id, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch booking types"
        )


@router.post("/bookings", response_model=Dict[str, Any], status_code=status.HTTP_201_CREATED)
async def create_public_booking(
    booking_data: PublicBookingCreate,
    request: Request,
    supabase: Client = Depends(get_supabase)
):
    """Create booking from public booking page"""
    # Apply rate limiting
    check_rate_limit(request)
    
    try:
        # Verify workspace exists
        workspace_response = (
            supabase.table("workspaces")
            .select("*")
            .eq("id", booking_data.workspace_id)
            .single()
            .execute()
        )
        
        if not workspace_response.data:
            logger.warning("workspace_not_found", workspace_id=booking_data.workspace_id)
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Workspace not found"
            )
        
        workspace = workspace_response.data
        
        # Verify booking type exists and belongs to workspace
        booking_type_service = BookingTypeService(supabase)
        booking_type = await booking_type_service.get_booking_type(booking_data.booking_type_id)
        
        if not booking_type:
            logger.warning("booking_type_not_found", booking_type_id=booking_data.booking_type_id)
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Booking type not found"
            )
        
        if booking_type["workspace_id"] != booking_data.workspace_id:
            logger.warning(
                "booking_type_workspace_mismatch",
                booking_type_id=booking_data.booking_type_id,
                expected_workspace=booking_data.workspace_id,
                actual_workspace=booking_type["workspace_id"]
            )
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Booking type does not belong to this workspace"
            )
        
        if not booking_type.get("is_active", True):
            logger.warning("booking_type_inactive", booking_type_id=booking_data.booking_type_id)
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Booking type is not active"
            )
        
        # Check if contact exists by email or phone
        contact = None
        if booking_data.contact_email:
            contact_response = (
                supabase.table("contacts")
                .select("*")
                .eq("workspace_id", booking_data.workspace_id)
                .eq("email", booking_data.contact_email)
                .limit(1)
                .execute()
            )
            if contact_response.data:
                contact = contact_response.data[0]
                logger.info("existing_contact_found", contact_id=contact["id"])
        
        # Create or update contact
        if not contact:
            contact_dict = {
                "workspace_id": booking_data.workspace_id,
                "name": booking_data.contact_name,
                "email": booking_data.contact_email,
                "phone": booking_data.contact_phone,
                "source": "booking_page",
            }
            contact_response = supabase.table("contacts").insert(contact_dict).execute()
            contact = contact_response.data[0]
            logger.info("contact_created", contact_id=contact["id"])
            
            # Create conversation for new contact
            conversation_data = {
                "workspace_id": booking_data.workspace_id,
                "contact_id": contact["id"],
                "unread_count": 1,
            }
            conversation_response = supabase.table("conversations").insert(conversation_data).execute()
            logger.info("conversation_created", conversation_id=conversation_response.data[0]["id"])
        else:
            # Update existing contact if needed
            update_dict = {}
            if booking_data.contact_name and booking_data.contact_name != contact.get("name"):
                update_dict["name"] = booking_data.contact_name
            if booking_data.contact_phone and booking_data.contact_phone != contact.get("phone"):
                update_dict["phone"] = booking_data.contact_phone
            
            if update_dict:
                supabase.table("contacts").update(update_dict).eq("id", contact["id"]).execute()
                logger.info("contact_updated", contact_id=contact["id"])
        
        # Combine date and time to create scheduled_at
        scheduled_at = f"{booking_data.booking_date}T{booking_data.start_time}:00"
        
        # Create booking
        booking_dict = {
            "workspace_id": booking_data.workspace_id,
            "booking_type_id": booking_data.booking_type_id,
            "contact_id": contact["id"],
            "scheduled_at": scheduled_at,
            "status": "pending",
            "notes": booking_data.notes,
        }
        
        booking_response = supabase.table("bookings").insert(booking_dict).execute()
        booking = booking_response.data[0]
        logger.info("booking_created", booking_id=booking["id"])
        
        # Send confirmation email if integration configured
        email_sent = False
        if booking_data.contact_email:
            try:
                from app.services.communication.email_provider import EmailService
                email_service = EmailService()
                
                # Format booking details for email
                scheduled_datetime = datetime.fromisoformat(scheduled_at)
                formatted_date = scheduled_datetime.strftime("%B %d, %Y at %I:%M %p")
                
                email_content = f"""
                <html>
                <body>
                    <h2>Booking Confirmation</h2>
                    <p>Dear {booking_data.contact_name},</p>
                    <p>Your booking has been confirmed!</p>
                    <h3>Booking Details:</h3>
                    <ul>
                        <li><strong>Service:</strong> {booking_type['name']}</li>
                        <li><strong>Date & Time:</strong> {formatted_date}</li>
                        <li><strong>Duration:</strong> {booking_type['duration_minutes']} minutes</li>
                        <li><strong>Location:</strong> {booking_type['location_type']}</li>
                    </ul>
                    {f'<p><strong>Notes:</strong> {booking_data.notes}</p>' if booking_data.notes else ''}
                    <p>If you need to make any changes, please contact us.</p>
                    <p>Thank you!</p>
                </body>
                </html>
                """
                
                await email_service.send_email(
                    to=booking_data.contact_email,
                    subject=f"Booking Confirmation - {booking_type['name']}",
                    content=email_content
                )
                email_sent = True
                logger.info("booking_confirmation_email_sent", booking_id=booking["id"])
            except Exception as email_error:
                logger.warning("booking_confirmation_email_failed", error=str(email_error), booking_id=booking["id"])
                # Don't fail the booking if email fails
        
        # Send notification to workspace owner
        try:
            # Get workspace owner
            owner_response = (
                supabase.table("users")
                .select("email")
                .eq("workspace_id", booking_data.workspace_id)
                .eq("role", "owner")
                .limit(1)
                .execute()
            )
            
            # Create alert for workspace owner
            alert_data = {
                "workspace_id": booking_data.workspace_id,
                "alert_type": "new_booking",
                "priority": "medium",
                "title": "New Booking",
                "message": f"New booking from {booking_data.contact_name} for {booking_type['name']} on {formatted_date}",
                "metadata": {"booking_id": booking["id"]},
            }
            supabase.table("alerts").insert(alert_data).execute()
            logger.info("owner_notification_created", booking_id=booking["id"])
            
            # Send email notification to owner if available
            if owner_response.data and owner_response.data[0].get("email"):
                try:
                    from app.services.communication.email_provider import EmailService
                    email_service = EmailService()
                    
                    owner_email_content = f"""
                    <html>
                    <body>
                        <h2>New Booking Notification</h2>
                        <p>You have a new booking!</p>
                        <h3>Booking Details:</h3>
                        <ul>
                            <li><strong>Client:</strong> {booking_data.contact_name}</li>
                            <li><strong>Email:</strong> {booking_data.contact_email or 'Not provided'}</li>
                            <li><strong>Phone:</strong> {booking_data.contact_phone or 'Not provided'}</li>
                            <li><strong>Service:</strong> {booking_type['name']}</li>
                            <li><strong>Date & Time:</strong> {formatted_date}</li>
                            <li><strong>Duration:</strong> {booking_type['duration_minutes']} minutes</li>
                            <li><strong>Location:</strong> {booking_type['location_type']}</li>
                        </ul>
                        {f'<p><strong>Notes:</strong> {booking_data.notes}</p>' if booking_data.notes else ''}
                    </body>
                    </html>
                    """
                    
                    await email_service.send_email(
                        to=owner_response.data[0]["email"],
                        subject=f"New Booking - {booking_type['name']}",
                        content=owner_email_content
                    )
                    logger.info("owner_notification_email_sent", booking_id=booking["id"])
                except Exception as owner_email_error:
                    logger.warning("owner_notification_email_failed", error=str(owner_email_error))
        except Exception as notification_error:
            logger.warning("owner_notification_failed", error=str(notification_error))
            # Don't fail the booking if notification fails
        
        return {
            "success": True,
            "booking": booking,
            "message": "Booking created successfully",
            "email_sent": email_sent
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("create_public_booking_failed", error=str(e), workspace_id=booking_data.workspace_id)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to create booking: {str(e)}"
        )


@router.get("/{slug}", response_model=WorkspacePublicResponse)
async def get_workspace_by_slug(
    slug: str,
    supabase: Client = Depends(get_supabase)
):
    """Get public workspace information by slug"""
    try:
        service = WorkspaceService(supabase)
        workspace = await service.get_by_slug(slug)
        
        # Track analytics event
        supabase.table("analytics_events").insert({
            "workspace_id": workspace["id"],
            "event_type": "workspace_view",
            "event_data": {"slug": slug}
        }).execute()
        
        return WorkspacePublicResponse(
            id=workspace["id"],
            name=workspace["name"],
            slug=workspace["slug"],
            logo_url=workspace.get("logo_url"),
            primary_color=workspace.get("primary_color", "#3b82f6"),
            secondary_color=workspace.get("secondary_color", "#8b5cf6"),
        )
    except Exception as e:
        logger.error("get_workspace_by_slug_failed", slug=slug, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workspace not found"
        )


@router.post("/{slug}/contact", response_model=ContactResponse, status_code=status.HTTP_201_CREATED)
async def submit_contact_form(
    slug: str,
    contact_data: ContactCreate,
    request: Request,
    supabase: Client = Depends(get_supabase)
):
    """Submit public contact form"""
    try:
        # Get workspace
        workspace_service = WorkspaceService(supabase)
        workspace = await workspace_service.get_by_slug(slug)
        
        # Create contact
        contact_dict = contact_data.model_dump()
        contact_dict["workspace_id"] = workspace["id"]
        contact_dict["source"] = "contact_form"
        contact_dict["source_url"] = f"/public/{slug}/contact"
        
        contact_response = supabase.table("contacts").insert(contact_dict).execute()
        contact = contact_response.data[0]
        
        # Create conversation
        conversation_data = {
            "workspace_id": workspace["id"],
            "contact_id": contact["id"],
            "unread_count": 1,
        }
        supabase.table("conversations").insert(conversation_data).execute()
        
        # Track analytics
        supabase.table("analytics_events").insert({
            "workspace_id": workspace["id"],
            "event_type": "contact_form_submit",
            "event_data": {"contact_id": contact["id"]},
            "ip_address": request.client.host if request.client else None,
            "user_agent": request.headers.get("user-agent"),
        }).execute()
        
        # Trigger welcome message automation
        send_welcome_message.delay(contact["id"], workspace["id"])
        
        logger.info("contact_form_submitted", workspace_id=workspace["id"], contact_id=contact["id"])
        
        return ContactResponse(**contact)
        
    except Exception as e:
        logger.error("submit_contact_form_failed", slug=slug, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/{slug}/booking-types", response_model=List[BookingTypeResponse])
async def get_booking_types(
    slug: str,
    request: Request,
    supabase: Client = Depends(get_supabase)
):
    """Get available booking types for workspace"""
    # Apply rate limiting
    check_rate_limit(request)
    
    try:
        workspace_service = WorkspaceService(supabase)
        workspace = await workspace_service.get_by_slug(slug)
        
        response = (
            supabase.table("booking_types")
            .select("*")
            .eq("workspace_id", workspace["id"])
            .eq("is_active", True)
            .execute()
        )
        
        return [BookingTypeResponse(**bt) for bt in response.data]
        
    except Exception as e:
        logger.error("get_booking_types_failed", slug=slug, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workspace not found"
        )


@router.get("/{slug}/availability")
async def get_availability(
    slug: str,
    booking_type_id: str,
    start_date: str,
    end_date: str,
    request: Request,
    supabase: Client = Depends(get_supabase)
):
    """Get available time slots for booking"""
    # Apply rate limiting
    check_rate_limit(request)
    
    try:
        workspace_service = WorkspaceService(supabase)
        workspace = await workspace_service.get_by_slug(slug)
        
        booking_service = BookingService(supabase)
        availability = await booking_service.get_availability(
            workspace["id"],
            booking_type_id,
            start_date,
            end_date
        )
        
        return availability
        
    except Exception as e:
        logger.error("get_availability_failed", slug=slug, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/{slug}/book", response_model=Dict[str, Any], status_code=status.HTTP_201_CREATED)
async def create_booking_by_slug(
    slug: str,
    booking_data: BookingCreate,
    request: Request,
    supabase: Client = Depends(get_supabase)
):
    """Create booking from public booking page using workspace slug"""
    # Apply rate limiting
    check_rate_limit(request)
    
    try:
        workspace_service = WorkspaceService(supabase)
        workspace = await workspace_service.get_by_slug(slug)
        
        # Check if contact exists by email or phone
        contact = None
        if booking_data.contact_email:
            contact_response = (
                supabase.table("contacts")
                .select("*")
                .eq("workspace_id", workspace["id"])
                .eq("email", booking_data.contact_email)
                .limit(1)
                .execute()
            )
            if contact_response.data:
                contact = contact_response.data[0]
        
        # Create contact if doesn't exist
        if not contact:
            contact_dict = {
                "workspace_id": workspace["id"],
                "name": booking_data.contact_name,
                "email": booking_data.contact_email,
                "phone": booking_data.contact_phone,
                "source": "booking_page",
                "source_url": f"/public/{slug}/book",
            }
            contact_response = supabase.table("contacts").insert(contact_dict).execute()
            contact = contact_response.data[0]
            
            # Create conversation for new contact
            conversation_data = {
                "workspace_id": workspace["id"],
                "contact_id": contact["id"],
            }
            supabase.table("conversations").insert(conversation_data).execute()
        
        # Create booking
        booking_service = BookingService(supabase)
        booking_dict = {
            "workspace_id": workspace["id"],
            "booking_type_id": booking_data.booking_type_id,
            "contact_id": contact["id"],
            "scheduled_at": booking_data.scheduled_at.isoformat() if hasattr(booking_data.scheduled_at, 'isoformat') else booking_data.scheduled_at,
            "status": "confirmed",
            "notes": booking_data.notes,
        }
        
        booking = await booking_service.create(booking_dict)
        
        # Track analytics
        supabase.table("analytics_events").insert({
            "workspace_id": workspace["id"],
            "event_type": "booking_created",
            "event_data": {
                "booking_id": booking["id"],
                "booking_type_id": booking_data.booking_type_id,
                "source": "public_page"
            },
            "ip_address": request.client.host if request.client else None,
            "user_agent": request.headers.get("user-agent"),
        }).execute()
        
        # Trigger automations
        send_booking_confirmation.delay(booking["id"])
        send_form_after_booking.delay(booking["id"])
        
        logger.info("public_booking_created", workspace_id=workspace["id"], booking_id=booking["id"])
        
        return {
            "success": True,
            "booking": booking,
            "message": "Booking created successfully"
        }
        
    except Exception as e:
        logger.error("create_public_booking_failed", slug=slug, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/form/{submission_id}/{token}", response_model=FormSubmissionResponse)
async def get_form_submission(
    submission_id: str,
    token: str,
    supabase: Client = Depends(get_supabase)
):
    """Get form submission by ID and token (for public form completion)"""
    try:
        response = (
            supabase.table("form_submissions")
            .select("*, form_templates(*), contacts(*)")
            .eq("id", submission_id)
            .eq("access_token", token)
            .single()
            .execute()
        )
        
        if not response.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Form submission not found"
            )
        
        return FormSubmissionResponse(**response.data)
        
    except Exception as e:
        logger.error("get_form_submission_failed", submission_id=submission_id, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Form submission not found"
        )


@router.post("/form/{submission_id}/{token}", response_model=FormSubmissionResponse)
async def submit_form(
    submission_id: str,
    token: str,
    form_data: FormSubmissionPublicCreate,
    supabase: Client = Depends(get_supabase)
):
    """Submit completed form"""
    try:
        # Verify token
        response = (
            supabase.table("form_submissions")
            .select("*")
            .eq("id", submission_id)
            .eq("access_token", token)
            .single()
            .execute()
        )
        
        if not response.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Form submission not found"
            )
        
        submission = response.data
        
        # Update submission
        update_data = {
            "data": form_data.data,
            "status": "completed",
            "submitted_at": datetime.utcnow().isoformat(),
        }
        
        updated_response = (
            supabase.table("form_submissions")
            .update(update_data)
            .eq("id", submission_id)
            .execute()
        )
        
        # Track analytics
        supabase.table("analytics_events").insert({
            "workspace_id": submission["workspace_id"],
            "event_type": "form_completed",
            "event_data": {"submission_id": submission_id}
        }).execute()
        
        logger.info("form_submitted", submission_id=submission_id)
        
        return FormSubmissionResponse(**updated_response.data[0])
        
    except Exception as e:
        logger.error("submit_form_failed", submission_id=submission_id, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/{slug}/public-form")
async def get_public_form(
    slug: str,
    supabase: Client = Depends(get_supabase)
):
    """Get public contact form configuration"""
    try:
        workspace_service = WorkspaceService(supabase)
        workspace = await workspace_service.get_by_slug(slug)
        
        response = (
            supabase.table("public_forms")
            .select("*")
            .eq("workspace_id", workspace["id"])
            .eq("is_active", True)
            .limit(1)
            .execute()
        )
        
        if not response.data:
            # Return default form structure
            return {
                "name": "Contact Us",
                "description": "Get in touch with us",
                "fields": [
                    {"name": "name", "type": "text", "label": "Name", "required": True},
                    {"name": "email", "type": "email", "label": "Email", "required": True},
                    {"name": "phone", "type": "tel", "label": "Phone", "required": False},
                    {"name": "message", "type": "textarea", "label": "Message", "required": False},
                ],
                "submit_button_text": "Submit",
                "success_message": "Thank you! We'll be in touch soon.",
            }
        
        return response.data[0]
        
    except Exception as e:
        logger.error("get_public_form_failed", slug=slug, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workspace not found"
        )



@router.get("/forms/view/{submission_id}")
async def view_form_submission(
    submission_id: str,
    supabase: Client = Depends(get_supabase)
):
    """View form submission details (public access for clients)"""
    try:
        # Get submission
        submission_response = (
            supabase.table("form_submissions")
            .select("*, form_templates(*), bookings(*, booking_types(*)), contacts(*)")
            .eq("id", submission_id)
            .single()
            .execute()
        )
        
        if not submission_response.data:
            raise HTTPException(status_code=404, detail="Form not found")
        
        submission = submission_response.data
        form_template = submission["form_templates"]
        
        # Track that form was viewed
        if not submission.get("viewed_at"):
            supabase.table("form_submissions").update({
                "viewed_at": datetime.utcnow().isoformat()
            }).eq("id", submission_id).execute()
        
        logger.info("form_viewed", submission_id=submission_id)
        
        return {
            "id": submission["id"],
            "form_name": form_template["name"],
            "form_description": form_template.get("description"),
            "file_url": form_template["file_url"],
            "file_type": form_template.get("file_type"),
            "status": submission["status"],
            "booking": submission.get("bookings"),
            "contact": submission.get("contacts")
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("view_form_submission_failed", submission_id=submission_id, error=str(e))
        raise HTTPException(status_code=500, detail="Failed to load form")


@router.post("/forms/track-download/{submission_id}")
async def track_form_download(
    submission_id: str,
    supabase: Client = Depends(get_supabase)
):
    """Track when a form is downloaded"""
    try:
        # Update download timestamp
        supabase.table("form_submissions").update({
            "downloaded_at": datetime.utcnow().isoformat()
        }).eq("id", submission_id).execute()
        
        logger.info("form_downloaded", submission_id=submission_id)
        
        return {"message": "Download tracked successfully"}
        
    except Exception as e:
        logger.error("track_form_download_failed", submission_id=submission_id, error=str(e))
        raise HTTPException(status_code=500, detail="Failed to track download")


@router.post("/forms/mark-complete/{submission_id}")
async def mark_form_complete(
    submission_id: str,
    supabase: Client = Depends(get_supabase)
):
    """Mark form as completed by client"""
    try:
        # Update status to completed
        supabase.table("form_submissions").update({
            "status": "completed",
            "submitted_at": datetime.utcnow().isoformat()
        }).eq("id", submission_id).execute()
        
        logger.info("form_completed", submission_id=submission_id)
        
        return {"message": "Form marked as complete"}
        
    except Exception as e:
        logger.error("mark_form_complete_failed", submission_id=submission_id, error=str(e))
        raise HTTPException(status_code=500, detail="Failed to mark form complete")
