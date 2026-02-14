"""Enums for the application"""
from enum import Enum


class UserRole(str, Enum):
    """User roles"""
    OWNER = "owner"
    STAFF = "staff"


class WorkspaceStatus(str, Enum):
    """Workspace status"""
    SETUP = "setup"
    ACTIVE = "active"
    SUSPENDED = "suspended"


class OnboardingStep(str, Enum):
    """Onboarding steps"""
    WORKSPACE_CREATED = "workspace_created"
    COMMUNICATION_SETUP = "communication_setup"
    CONTACT_FORM_CREATED = "contact_form_created"
    BOOKING_SETUP = "booking_setup"
    FORMS_SETUP = "forms_setup"
    INVENTORY_SETUP = "inventory_setup"
    STAFF_ADDED = "staff_added"
    ACTIVATED = "activated"


class BookingStatus(str, Enum):
    """Booking status"""
    PENDING = "pending"
    CONFIRMED = "confirmed"
    COMPLETED = "completed"
    NO_SHOW = "no_show"
    CANCELLED = "cancelled"


class FormStatus(str, Enum):
    """Form completion status"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    OVERDUE = "overdue"


class CommunicationChannel(str, Enum):
    """Communication channels"""
    EMAIL = "email"
    SMS = "sms"


class MessageType(str, Enum):
    """Message types"""
    AUTOMATED = "automated"
    MANUAL = "manual"


class AlertType(str, Enum):
    """Alert types"""
    MISSED_MESSAGE = "missed_message"
    UNCONFIRMED_BOOKING = "unconfirmed_booking"
    OVERDUE_FORM = "overdue_form"
    LOW_INVENTORY = "low_inventory"
    CRITICAL_INVENTORY = "critical_inventory"


class AlertPriority(str, Enum):
    """Alert priority levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class IntegrationProvider(str, Enum):
    """Integration providers"""
    RESEND = "resend"
    SENDGRID = "sendgrid"
    TWILIO = "twilio"
    GOOGLE_CALENDAR = "google_calendar"


class IntegrationStatus(str, Enum):
    """Integration status"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    ERROR = "error"
