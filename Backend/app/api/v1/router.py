"""Main API router"""
from fastapi import APIRouter

from app.api.v1.endpoints import (
    auth,
    workspaces,
    bookings,
    contacts,
    messages,
    forms,
    inventory,
    dashboard,
    integrations,
    public,
)

api_router = APIRouter()

# Public endpoints (no authentication)
api_router.include_router(public.router, prefix="/public", tags=["Public"])

# Protected endpoints (authentication required)
api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(workspaces.router, prefix="/workspaces", tags=["Workspaces"])
api_router.include_router(bookings.router, prefix="/bookings", tags=["Bookings"])
api_router.include_router(contacts.router, prefix="/contacts", tags=["Contacts"])
api_router.include_router(messages.router, prefix="/messages", tags=["Messages"])
api_router.include_router(forms.router, prefix="/forms", tags=["Forms"])
api_router.include_router(inventory.router, prefix="/inventory", tags=["Inventory"])
api_router.include_router(dashboard.router, prefix="/dashboard", tags=["Dashboard"])
api_router.include_router(integrations.router, prefix="/integrations", tags=["Integrations"])
