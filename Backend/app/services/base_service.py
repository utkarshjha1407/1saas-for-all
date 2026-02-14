"""Base service class with common functionality"""
from abc import ABC
from supabase import Client
import structlog
from typing import Optional, Dict, Any, List

from app.core.exceptions import NotFoundException, IntegrationException

logger = structlog.get_logger()


class BaseService(ABC):
    """Base service with common database operations"""
    
    def __init__(self, supabase: Client, table_name: str):
        self.supabase = supabase
        self.table_name = table_name
        self.logger = logger.bind(service=self.__class__.__name__)
    
    async def get_by_id(self, id: str) -> Optional[Dict[str, Any]]:
        """Get record by ID"""
        try:
            response = self.supabase.table(self.table_name).select("*").eq("id", id).execute()
            
            if not response.data:
                raise NotFoundException(f"{self.table_name} with id {id} not found")
            
            return response.data[0]
        except Exception as e:
            self.logger.error("get_by_id_failed", id=id, error=str(e))
            raise
    
    async def get_all(
        self,
        filters: Optional[Dict[str, Any]] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """Get all records with optional filters"""
        try:
            query = self.supabase.table(self.table_name).select("*")
            
            if filters:
                for key, value in filters.items():
                    query = query.eq(key, value)
            
            response = query.range(offset, offset + limit - 1).execute()
            return response.data
        except Exception as e:
            self.logger.error("get_all_failed", error=str(e))
            raise
    
    async def create(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create new record"""
        try:
            response = self.supabase.table(self.table_name).insert(data).execute()
            
            if not response.data:
                raise IntegrationException("Failed to create record", service="Supabase")
            
            self.logger.info("record_created", table=self.table_name)
            return response.data[0]
        except Exception as e:
            self.logger.error("create_failed", error=str(e))
            raise
    
    async def update(self, id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Update record"""
        try:
            response = (
                self.supabase.table(self.table_name)
                .update(data)
                .eq("id", id)
                .execute()
            )
            
            if not response.data:
                raise NotFoundException(f"{self.table_name} with id {id} not found")
            
            self.logger.info("record_updated", table=self.table_name, id=id)
            return response.data[0]
        except Exception as e:
            self.logger.error("update_failed", id=id, error=str(e))
            raise
    
    async def delete(self, id: str) -> bool:
        """Delete record"""
        try:
            response = self.supabase.table(self.table_name).delete().eq("id", id).execute()
            
            self.logger.info("record_deleted", table=self.table_name, id=id)
            return True
        except Exception as e:
            self.logger.error("delete_failed", id=id, error=str(e))
            raise
