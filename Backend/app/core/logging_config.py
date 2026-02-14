"""Logging configuration"""
import structlog
import logging
from app.core.config import settings


def setup_logging():
    """Configure structured logging"""
    
    logging.basicConfig(
        format="%(message)s",
        level=logging.INFO if not settings.DEBUG else logging.DEBUG,
    )
    
    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.processors.add_log_level,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.JSONRenderer() if settings.ENVIRONMENT == "production"
            else structlog.dev.ConsoleRenderer(),
        ],
        wrapper_class=structlog.make_filtering_bound_logger(logging.INFO),
        context_class=dict,
        logger_factory=structlog.PrintLoggerFactory(),
        cache_logger_on_first_use=True,
    )
