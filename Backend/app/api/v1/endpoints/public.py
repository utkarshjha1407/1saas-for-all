"""Public endpoints (no authentication required)"""
from fastapi import APIRouter, Depends, HTTPException, status, Request
from supabase import Client
from typing import List, Dict, Any
from datetime import datetime, timedelta
import structlog

from app.db.supabase_client import get_supabase
from app.schemas.workspace import WorkspacePublicResponse
from app.schemas.contact import ContactCreate, ContactResponse
from app.schemas.booking import BookingCreate, BookingResponse, BookingTypeResponse
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
    supabase: Client = Depends(get_supabase)
):
    """Get available booking types for workspace"""
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
    supabase: Client = Depends(get_supabase)
):
    """Get available time slots for booking"""
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


@router.post("/{slug}/book", response_model=BookingResponse, status_code=status.HTTP_201_CREATED)
async def create_public_booking(
    slug: str,
    booking_data: BookingCreate,
    request: Request,
    supabase: Client = Depends(get_supabase)
):
    """Create booking from public booking page"""
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
            "scheduled_at": booking_data.scheduled_at,
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
        
        return BookingResponse(**booking)
        
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
