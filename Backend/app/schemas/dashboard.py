"""Dashboard schemas"""
from pydantic import BaseModel
from typing import List
from datetime import datetime


class BookingOverview(BaseModel):
    """Booking overview for dashboard"""
    today_count: int
    upcoming_count: int
    completed_count: int
    no_show_count: int


class LeadOverview(BaseModel):
    """Lead overview for dashboard"""
    new_inquiries: int
    ongoing_conversations: int
    unanswered_messages: int


class FormOverview(BaseModel):
    """Form overview for dashboard"""
    pending_count: int
    overdue_count: int
    completed_count: int


class InventoryOverview(BaseModel):
    """Inventory overview for dashboard"""
    low_stock_items: int
    critical_items: int


class DashboardStats(BaseModel):
    """Dashboard statistics"""
    bookings: BookingOverview
    leads: LeadOverview
    forms: FormOverview
    inventory: InventoryOverview
    total_alerts: int
    critical_alerts: int
    generated_at: datetime
