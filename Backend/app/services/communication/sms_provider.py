"""SMS provider implementation"""
from typing import Dict, Any
from twilio.rest import Client

from app.core.config import settings
from app.core.exceptions import IntegrationException
from app.services.communication.base_provider import CommunicationProvider


class TwilioSMSProvider(CommunicationProvider):
    """Twilio SMS provider"""
    
    def __init__(self):
        super().__init__("Twilio")
        
        if not all([settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN, settings.TWILIO_PHONE_NUMBER]):
            raise IntegrationException("Twilio credentials not configured", service="Twilio")
        
        self.client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
        self.from_number = settings.TWILIO_PHONE_NUMBER
    
    async def send(self, to: str, subject: str, content: str, **kwargs) -> Dict[str, Any]:
        """Send SMS via Twilio"""
        try:
            message = self.client.messages.create(
                body=content,
                from_=self.from_number,
                to=to
            )
            
            self.logger.info("sms_sent", recipient=to, message_sid=message.sid)
            return {"success": True, "message_sid": message.sid}
        except Exception as e:
            await self.log_failure(e, to)
            raise IntegrationException(f"Failed to send SMS: {str(e)}", service="Twilio")
    
    async def verify_connection(self) -> bool:
        """Verify Twilio connection"""
        try:
            # Fetch account to verify credentials
            account = self.client.api.accounts(settings.TWILIO_ACCOUNT_SID).fetch()
            return account.status == "active"
        except Exception:
            return False


class SMSService:
    """SMS service"""
    
    def __init__(self):
        self.provider = None
        
        if all([settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN]):
            try:
                self.provider = TwilioSMSProvider()
            except Exception:
                pass
    
    async def send_sms(self, to: str, content: str) -> Dict[str, Any]:
        """Send SMS"""
        if not self.provider:
            raise IntegrationException("No SMS provider configured", service="SMS")
        
        return await self.provider.send(to, "", content)
