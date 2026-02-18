"""Contact form service for managing public contact forms"""
from typing import Dict, Any, Optional
from supabase import Client
import structlog

from app.services.base_service import BaseService
from app.core.exceptions import ValidationException

logger = structlog.get_logger()


class ContactFormService(BaseService):
    """Service for managing contact forms"""
    
    def __init__(self, supabase: Client):
        super().__init__(supabase, "public_forms")
        self.supabase = supabase
    
    async def get_workspace_form(self, workspace_id: str) -> Optional[Dict[str, Any]]:
        """Get active contact form for workspace"""
        response = (
            self.supabase.table(self.table_name)
            .select("*")
            .eq("workspace_id", workspace_id)
            .eq("is_active", True)
            .limit(1)
            .execute()
        )
        
        if response.data:
            return response.data[0]
        return None
    
    async def create_or_update_form(
        self, 
        workspace_id: str, 
        form_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Create or update contact form for workspace"""
        existing = await self.get_workspace_form(workspace_id)
        
        form_config = {
            "workspace_id": workspace_id,
            "name": form_data.get("name", "Contact Us"),
            "description": form_data.get("description", "Get in touch with us"),
            "fields": form_data.get("fields", self._get_default_fields()),
            "submit_button_text": form_data.get("submit_button_text", "Submit"),
            "success_message": form_data.get("success_message", "Thank you! We'll be in touch soon."),
            "welcome_message": form_data.get("welcome_message", "Thank you for contacting us! We'll get back to you shortly."),
            "is_active": True,
        }
        
        if existing:
            # Update existing form
            response = (
                self.supabase.table(self.table_name)
                .update(form_config)
                .eq("id", existing["id"])
                .execute()
            )
            logger.info("contact_form_updated", workspace_id=workspace_id, form_id=existing["id"])
            return response.data[0]
        else:
            # Create new form
            response = (
                self.supabase.table(self.table_name)
                .insert(form_config)
                .execute()
            )
            logger.info("contact_form_created", workspace_id=workspace_id, form_id=response.data[0]["id"])
            return response.data[0]
    
    def _get_default_fields(self) -> list:
        """Get default form fields"""
        return [
            {
                "name": "name",
                "type": "text",
                "label": "Name",
                "placeholder": "Your name",
                "required": True,
                "order": 1
            },
            {
                "name": "email",
                "type": "email",
                "label": "Email",
                "placeholder": "your@email.com",
                "required": True,
                "order": 2
            },
            {
                "name": "phone",
                "type": "tel",
                "label": "Phone",
                "placeholder": "+1234567890",
                "required": False,
                "order": 3
            },
            {
                "name": "message",
                "type": "textarea",
                "label": "Message",
                "placeholder": "How can we help you?",
                "required": False,
                "order": 4
            }
        ]
    
    async def get_form_submissions_count(self, workspace_id: str) -> int:
        """Get count of form submissions for workspace"""
        response = (
            self.supabase.table("contacts")
            .select("id", count="exact")
            .eq("workspace_id", workspace_id)
            .eq("source", "contact_form")
            .execute()
        )
        return response.count or 0
    
    async def validate_form_config(self, form_data: Dict[str, Any]) -> bool:
        """Validate form configuration"""
        # Check required fields
        if not form_data.get("name"):
            raise ValidationException("Form name is required")
        
        fields = form_data.get("fields", [])
        if not fields:
            raise ValidationException("At least one field is required")
        
        # Check that at least email or phone is required
        has_contact_method = False
        for field in fields:
            if field.get("name") in ["email", "phone"] and field.get("required"):
                has_contact_method = True
                break
        
        if not has_contact_method:
            raise ValidationException("At least one contact method (email or phone) must be required")
        
        return True
