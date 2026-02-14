"""Base communication provider interface"""
from abc import ABC, abstractmethod
from typing import Dict, Any
import structlog

logger = structlog.get_logger()


class CommunicationProvider(ABC):
    """Abstract base class for communication providers"""
    
    def __init__(self, provider_name: str):
        self.provider_name = provider_name
        self.logger = logger.bind(provider=provider_name)
    
    @abstractmethod
    async def send(self, to: str, subject: str, content: str, **kwargs) -> Dict[str, Any]:
        """Send message through provider"""
        pass
    
    @abstractmethod
    async def verify_connection(self) -> bool:
        """Verify provider connection"""
        pass
    
    async def log_failure(self, error: Exception, recipient: str):
        """Log communication failure"""
        self.logger.error(
            "communication_failed",
            provider=self.provider_name,
            recipient=recipient,
            error=str(error)
        )
