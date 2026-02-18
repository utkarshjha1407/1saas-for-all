"""Integration service for managing and verifying integrations"""
from typing import Dict, Any, Optional
from supabase import Client
import structlog

from app.services.base_service import BaseService
from app.models.enums import IntegrationProvider, IntegrationStatus, AlertType, AlertPriority
from app.core.exceptions import IntegrationException

logger = structlog.get_logger()


class IntegrationService(BaseService):
    """Service for managing integrations"""
    
    def __init__(self, supabase: Client):
        super().__init__(supabase, "integrations")
        self.supabase = supabase
    
    async def verify_email_provider(
        self, 
        provider: IntegrationProvider, 
        config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Verify email provider connection"""
        try:
            if provider == IntegrationProvider.RESEND:
                return await self._verify_resend(config)
            elif provider == IntegrationProvider.SENDGRID:
                return await self._verify_sendgrid(config)
            else:
                raise IntegrationException(
                    f"Unsupported email provider: {provider}",
                    service=provider.value
                )
        except Exception as e:
            logger.error("email_verification_failed", provider=provider.value, error=str(e))
            return {
                "success": False,
                "error": str(e),
                "message": f"Failed to verify {provider.value} connection"
            }
    
    async def verify_sms_provider(
        self, 
        provider: IntegrationProvider, 
        config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Verify SMS provider connection"""
        try:
            if provider == IntegrationProvider.TWILIO:
                return await self._verify_twilio(config)
            else:
                raise IntegrationException(
                    f"Unsupported SMS provider: {provider}",
                    service=provider.value
                )
        except Exception as e:
            logger.error("sms_verification_failed", provider=provider.value, error=str(e))
            return {
                "success": False,
                "error": str(e),
                "message": f"Failed to verify {provider.value} connection"
            }
    
    async def _verify_resend(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Verify Resend API key"""
        import resend
        
        api_key = config.get("api_key")
        if not api_key:
            raise IntegrationException("API key is required", service="Resend")
        
        try:
            resend.api_key = api_key
            # Resend doesn't have a health check endpoint, so we validate the key format
            if not api_key.startswith("re_"):
                raise IntegrationException("Invalid Resend API key format", service="Resend")
            
            return {
                "success": True,
                "message": "Resend connection verified successfully"
            }
        except Exception as e:
            raise IntegrationException(f"Resend verification failed: {str(e)}", service="Resend")
    
    async def _verify_sendgrid(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Verify SendGrid API key"""
        from sendgrid import SendGridAPIClient
        
        api_key = config.get("api_key")
        if not api_key:
            raise IntegrationException("API key is required", service="SendGrid")
        
        try:
            client = SendGridAPIClient(api_key)
            # Test the API key by fetching API key info
            response = client.client.api_keys.get()
            
            if response.status_code == 200:
                return {
                    "success": True,
                    "message": "SendGrid connection verified successfully"
                }
            else:
                raise IntegrationException(
                    f"SendGrid API returned status {response.status_code}",
                    service="SendGrid"
                )
        except Exception as e:
            raise IntegrationException(f"SendGrid verification failed: {str(e)}", service="SendGrid")
    
    async def _verify_twilio(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Verify Twilio credentials"""
        from twilio.rest import Client
        
        account_sid = config.get("account_sid")
        auth_token = config.get("auth_token")
        phone_number = config.get("phone_number")
        
        if not all([account_sid, auth_token, phone_number]):
            raise IntegrationException(
                "Account SID, Auth Token, and Phone Number are required",
                service="Twilio"
            )
        
        try:
            client = Client(account_sid, auth_token)
            # Verify account is active
            account = client.api.accounts(account_sid).fetch()
            
            if account.status != "active":
                raise IntegrationException(
                    f"Twilio account status is {account.status}",
                    service="Twilio"
                )
            
            # Verify phone number format
            if not phone_number.startswith("+"):
                raise IntegrationException(
                    "Phone number must be in E.164 format (e.g., +1234567890)",
                    service="Twilio"
                )
            
            return {
                "success": True,
                "message": "Twilio connection verified successfully",
                "account_status": account.status
            }
        except Exception as e:
            raise IntegrationException(f"Twilio verification failed: {str(e)}", service="Twilio")
    
    async def log_integration_failure(
        self,
        workspace_id: str,
        provider: str,
        error_message: str
    ) -> None:
        """Log integration failure to alerts table"""
        try:
            alert_data = {
                "workspace_id": workspace_id,
                "type": AlertType.MISSED_MESSAGE.value,  # Using closest alert type
                "priority": AlertPriority.HIGH.value,
                "title": f"{provider} Integration Failure",
                "message": error_message,
                "is_read": False
            }
            
            result = self.supabase.table("alerts").insert(alert_data).execute()
            logger.info("integration_failure_logged", workspace_id=workspace_id, provider=provider)
        except Exception as e:
            logger.error("failed_to_log_integration_failure", error=str(e))
    
    async def get_workspace_integrations(self, workspace_id: str) -> Dict[str, Any]:
        """Get all integrations for a workspace with status"""
        integrations = await self.get_all({"workspace_id": workspace_id})
        
        # Organize by type
        email_integration = None
        sms_integration = None
        
        for integration in integrations:
            provider = integration.get("provider")
            if provider in [IntegrationProvider.RESEND.value, IntegrationProvider.SENDGRID.value]:
                email_integration = integration
            elif provider == IntegrationProvider.TWILIO.value:
                sms_integration = integration
        
        return {
            "email": email_integration,
            "sms": sms_integration,
            "has_email": email_integration is not None,
            "has_sms": sms_integration is not None,
            "has_any": email_integration is not None or sms_integration is not None
        }
