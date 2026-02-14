"""Security utilities for authentication and authorization"""
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
import bcrypt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from app.core.config import settings
from app.schemas.auth import TokenData
from app.models.enums import UserRole

security = HTTPBearer()


def hash_password(password: str) -> str:
    """Hash password with bcrypt
    
    Returns a bcrypt hash string (starts with $2b$ or $2a$)
    This is stored directly in the database - Supabase does NOT hash it again.
    """
    if not password or not isinstance(password, str):
        raise ValueError("Password must be a non-empty string")
    
    # Check password length in bytes (bcrypt limit is 72 bytes)
    password_bytes = password.encode('utf-8')
    if len(password_bytes) > 72:
        raise ValueError("Password is too long. Please use a password with 72 characters or less.")
    
    try:
        # Generate salt and hash password using bcrypt directly
        salt = bcrypt.gensalt()
        hashed_bytes = bcrypt.hashpw(password_bytes, salt)
        hashed = hashed_bytes.decode('utf-8')
        
        # Verify the hash format (should start with $2b$ or $2a$)
        if not hashed or not hashed.startswith(('$2a$', '$2b$', '$2y$')):
            raise ValueError(f"Invalid hash format generated: {hashed[:20] if hashed else 'None'}...")
        
        return hashed
    except Exception as e:
        error_msg = str(e)
        raise ValueError(f"Password hashing failed: {error_msg}") from e


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password against bcrypt hash"""
    try:
        password_bytes = plain_password.encode('utf-8')
        hash_bytes = hashed_password.encode('utf-8')
        return bcrypt.checkpw(password_bytes, hash_bytes)
    except Exception as e:
        return False


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create JWT access token"""
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire, "type": "access"})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def create_refresh_token(data: dict) -> str:
    """Create JWT refresh token"""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire, "type": "refresh"})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def decode_token(token: str) -> TokenData:
    """Decode and validate JWT token"""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id: str = payload.get("sub")
        email: str = payload.get("email")
        role: str = payload.get("role")
        workspace_id: str = payload.get("workspace_id")
        
        if user_id is None or email is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials",
            )
        
        return TokenData(
            user_id=user_id,
            email=email,
            role=UserRole(role),
            workspace_id=workspace_id
        )
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
        )


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> TokenData:
    """Get current authenticated user"""
    token = credentials.credentials
    return decode_token(token)


async def require_owner(current_user: TokenData = Depends(get_current_user)) -> TokenData:
    """Require owner role"""
    if current_user.role != UserRole.OWNER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Owner access required",
        )
    return current_user


async def require_staff_or_owner(
    current_user: TokenData = Depends(get_current_user)
) -> TokenData:
    """Require staff or owner role"""
    if current_user.role not in [UserRole.OWNER, UserRole.STAFF]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Staff or owner access required",
        )
    return current_user
