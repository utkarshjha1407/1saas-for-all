"""Authentication schemas"""
import re
from pydantic import BaseModel, EmailStr, Field, field_validator
from app.models.enums import UserRole


class UserRegister(BaseModel):
    """User registration schema"""
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=128, description="Password must be at least 8 characters with a symbol")
    full_name: str = Field(..., min_length=1, max_length=255)
    workspace_name: str = Field(..., min_length=1, max_length=255)
    
    @field_validator('password')
    @classmethod
    def validate_password_strength(cls, v: str) -> str:
        """Validate password strength: 8+ chars, at least one symbol"""
        # Check minimum length
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters long.")
        
        # Check for at least one symbol (special character)
        # Symbols: !@#$%^&*()_+-=[]{}|;:,.<>?/~`
        if not re.search(r'[!@#$%^&*()_+\-=\[\]{}|;:,.<>?/~`]', v):
            raise ValueError("Password must contain at least one symbol (!@#$%^&*()_+-=[]{}|;:,.<>?/~`).")
        
        # Note: Bcrypt has a 72-byte limit, but we let it handle that naturally
        # Most passwords won't hit this limit (72 ASCII characters = 72 bytes)
        # If a password exceeds 72 bytes, bcrypt will raise an error which we'll catch
        
        return v


class UserLogin(BaseModel):
    """User login schema"""
    email: EmailStr
    password: str


class Token(BaseModel):
    """Token response schema"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    """Token data schema"""
    user_id: str
    email: str
    role: UserRole
    workspace_id: str


class UserResponse(BaseModel):
    """User response schema"""
    id: str
    email: str
    full_name: str
    role: UserRole
    workspace_id: str
    is_active: bool
    
    class Config:
        from_attributes = True
