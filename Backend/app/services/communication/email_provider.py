"""Email provider implementations"""
from typing import Dict, Any, Optional
import resend
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

from app.core.config import settings
from app.core.exceptions import IntegrationException
from app.services.communication.base_provider import CommunicationProvider


class ResendEmailProvider(CommunicationProvider):
    """Resend email provider"""
    
    def __init__(self):
        super().__init__("Resend")
        if not settings.RESEND_API_KEY:
            raise IntegrationException("Resend API key not configured", service="Resend")
        resend.api_key = settings.RESEND_API_KEY
    
    async def send(self, to: str, subject: str, content: str, **kwargs) -> Dict[str, Any]:
        """Send email via Resend"""
        try:
            from_email = kwargs.get("from_email", settings.CORS_ORIGINS[0])
            
            response = resend.Emails.send({
                "from": from_email,
                "to": to,
                "subject": subject,
                "html": content,
            })
            
            self.logger.info("email_sent", recipient=to, provider="Resend")
            return {"success": True, "message_id": response.get("id")}
        except Exception as e:
            await self.log_failure(e, to)
            raise IntegrationException(f"Failed to send email: {str(e)}", service="Resend")
    
    async def verify_connection(self) -> bool:
        """Verify Resend connection"""
        try:
            # Resend doesn't have a dedicated health check, so we check if API key is set
            return bool(settings.RESEND_API_KEY)
        except Exception:
            return False


class SendGridEmailProvider(CommunicationProvider):
    """SendGrid email provider"""
    
    def __init__(self):
        super().__init__("SendGrid")
        if not settings.SENDGRID_API_KEY:
            raise IntegrationException("SendGrid API key not configured", service="SendGrid")
        self.client = SendGridAPIClient(settings.SENDGRID_API_KEY)
    
    async def send(self, to: str, subject: str, content: str, **kwargs) -> Dict[str, Any]:
        """Send email via SendGrid"""
        try:
            from_email = kwargs.get("from_email", settings.CORS_ORIGINS[0])
            
            message = Mail(
                from_email=from_email,
                to_emails=to,
                subject=subject,
                html_content=content
            )
            
            response = self.client.send(message)
            
            self.logger.info("email_sent", recipient=to, provider="SendGrid")
            return {"success": True, "status_code": response.status_code}
        except Exception as e:
            await self.log_failure(e, to)
            raise IntegrationException(f"Failed to send email: {str(e)}", service="SendGrid")
    
    async def verify_connection(self) -> bool:
        """Verify SendGrid connection"""
        try:
            # Simple API key validation
            return bool(self.client)
        except Exception:
            return False


class EmailService:
    """Email service with fallback support"""
    
    def __init__(self):
        self.providers = []
        
        # Initialize available providers
        if settings.RESEND_API_KEY:
            try:
                self.providers.append(ResendEmailProvider())
            except Exception:
                pass
        
        if settings.SENDGRID_API_KEY:
            try:
                self.providers.append(SendGridEmailProvider())
            except Exception:
                pass
        
        if not self.providers:
            raise IntegrationException("No email provider configured")
    
    async def send_email(self, to: str, subject: str, content: str, **kwargs) -> Dict[str, Any]:
        """Send email with fallback to next provider on failure"""
        last_error = None
        
        for provider in self.providers:
            try:
                return await provider.send(to, subject, content, **kwargs)
            except Exception as e:
                last_error = e
                continue
        
        # All providers failed
        raise IntegrationException(
            f"All email providers failed. Last error: {str(last_error)}",
            service="Email"
        )
