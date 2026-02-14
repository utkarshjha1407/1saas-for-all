"""Custom exceptions"""
from fastapi import status


class AppException(Exception):
    """Base application exception"""
    
    def __init__(
        self,
        message: str,
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
        error_code: str = "APP_ERROR",
    ):
        self.message = message
        self.status_code = status_code
        self.error_code = error_code
        super().__init__(self.message)


class NotFoundException(AppException):
    """Resource not found"""
    
    def __init__(self, message: str = "Resource not found"):
        super().__init__(
            message=message,
            status_code=status.HTTP_404_NOT_FOUND,
            error_code="NOT_FOUND",
        )


class UnauthorizedException(AppException):
    """Unauthorized access"""
    
    def __init__(self, message: str = "Unauthorized"):
        super().__init__(
            message=message,
            status_code=status.HTTP_401_UNAUTHORIZED,
            error_code="UNAUTHORIZED",
        )


class ForbiddenException(AppException):
    """Forbidden access"""
    
    def __init__(self, message: str = "Forbidden"):
        super().__init__(
            message=message,
            status_code=status.HTTP_403_FORBIDDEN,
            error_code="FORBIDDEN",
        )


class ValidationException(AppException):
    """Validation error"""
    
    def __init__(self, message: str = "Validation error"):
        super().__init__(
            message=message,
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            error_code="VALIDATION_ERROR",
        )


class ConflictException(AppException):
    """Resource conflict"""
    
    def __init__(self, message: str = "Resource conflict"):
        super().__init__(
            message=message,
            status_code=status.HTTP_409_CONFLICT,
            error_code="CONFLICT",
        )


class IntegrationException(AppException):
    """External integration error"""
    
    def __init__(self, message: str = "Integration error", service: str = ""):
        super().__init__(
            message=f"{service}: {message}" if service else message,
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            error_code="INTEGRATION_ERROR",
        )
