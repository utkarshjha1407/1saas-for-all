"""Alert schemas"""
from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime
from app.models.enums import AlertType, AlertPriority


class AlertResponse(BaseModel):
    """Alert response schema"""
    id: str
    workspace_id: str
    alert_type: AlertType
    priority: AlertPriority
    title: str
    message: str
    metadata: Dict[str, Any]
    is_read: bool
    is_resolved: bool
    created_at: datetime
    
    class Config:
        from_attributes = True
