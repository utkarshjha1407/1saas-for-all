"""Celery application configuration"""
from celery import Celery
from app.core.config import settings

celery_app = Celery(
    "careops",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
    include=["app.tasks.automation_tasks"]
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=300,
    task_soft_time_limit=240,
)

# Celery Beat Schedule for periodic tasks
celery_app.conf.beat_schedule = {
    "check-overdue-forms": {
        "task": "app.tasks.automation_tasks.check_overdue_forms",
        "schedule": 3600.0,  # Every hour
    },
    "send-booking-reminders": {
        "task": "app.tasks.automation_tasks.send_booking_reminders",
        "schedule": 1800.0,  # Every 30 minutes
    },
    "check-inventory-levels": {
        "task": "app.tasks.automation_tasks.check_inventory_levels",
        "schedule": 3600.0,  # Every hour
    },
}
