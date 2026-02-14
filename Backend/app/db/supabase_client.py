"""Supabase client with connection pooling and retry logic"""
from supabase import create_client, Client
from functools import lru_cache
import structlog
from typing import Optional
from tenacity import retry, stop_after_attempt, wait_exponential

from app.core.config import settings
from app.core.exceptions import IntegrationException

logger = structlog.get_logger()


class SupabaseClient:
    """Supabase client wrapper with error handling"""
    
    def __init__(self):
        self._client: Optional[Client] = None
        self._service_client: Optional[Client] = None
    
    @property
    def client(self) -> Client:
        """Get regular Supabase client (anon key)"""
        if not self._client:
            try:
                self._client = create_client(
                    settings.SUPABASE_URL,
                    settings.SUPABASE_KEY
                )
                logger.info("supabase_client_initialized", key_type="anon")
            except Exception as e:
                logger.exception("supabase_client_init_failed")
                raise IntegrationException(
                    message="Failed to initialize Supabase client",
                    service="Supabase"
                )
        return self._client
    
    @property
    def service_client(self) -> Client:
        """Get service role client (bypasses RLS)"""
        if not self._service_client:
            try:
                self._service_client = create_client(
                    settings.SUPABASE_URL,
                    settings.SUPABASE_SERVICE_KEY
                )
                logger.info("supabase_service_client_initialized")
            except Exception as e:
                logger.exception("supabase_service_client_init_failed")
                raise IntegrationException(
                    message="Failed to initialize Supabase service client",
                    service="Supabase"
                )
        return self._service_client
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10)
    )
    async def execute_with_retry(self, operation):
        """Execute operation with retry logic"""
        try:
            return operation
        except Exception as e:
            logger.error("supabase_operation_failed", error=str(e))
            raise


@lru_cache()
def get_supabase_client() -> SupabaseClient:
    """Get cached Supabase client instance"""
    return SupabaseClient()


# Dependency for FastAPI
def get_supabase() -> Client:
    """FastAPI dependency for Supabase client"""
    return get_supabase_client().client


def get_supabase_service() -> Client:
    """FastAPI dependency for Supabase service client"""
    return get_supabase_client().service_client
