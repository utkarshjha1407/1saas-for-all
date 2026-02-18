"""Authentication endpoints"""
from fastapi import APIRouter, Depends, HTTPException, status
from supabase import Client
import structlog

from app.db.supabase_client import get_supabase, get_supabase_service
from app.schemas.auth import UserRegister, UserLogin, Token, UserResponse
from app.core.security import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
    get_current_user,
)
from app.schemas.auth import TokenData
from app.models.enums import UserRole

logger = structlog.get_logger()
router = APIRouter()


@router.post("/register", response_model=Token, status_code=status.HTTP_201_CREATED)
async def register(
    user_data: UserRegister,
    supabase: Client = Depends(get_supabase_service)
):
    """Register new user and create workspace"""
    try:
        # Check if user exists
        existing = supabase.table("users").select("id").eq("email", user_data.email).execute()
        
        if existing.data:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Email already registered"
            )
        
        # Create user first without workspace
        try:
            # Hash the password using bcrypt
            hashed_password = hash_password(user_data.password)
            logger.debug("password_hashed", password_length=len(user_data.password), hash_length=len(hashed_password), hash_prefix=hashed_password[:20] if hashed_password else None)
        except ValueError as e:
            # Password validation error (e.g., too long for bcrypt)
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )
        
        # Prepare user data for insertion
        # IMPORTANT: We're storing the bcrypt hash directly - Supabase does NOT hash it again
        # Supabase Auth is NOT being used - we're using our own custom authentication
        user_data_dict = {
            "email": user_data.email,
            "password_hash": hashed_password,  # This is already a bcrypt hash string
            "full_name": user_data.full_name,
            "role": UserRole.OWNER.value,
            "is_active": True,
            "workspace_id": None,
        }
        logger.info("inserting_user", email=user_data.email, hash_format=hashed_password[:10] if hashed_password else None)
        
        try:
            user = supabase.table("users").insert(user_data_dict).execute()
        except Exception as e:
            logger.error("supabase_insert_error", error=str(e), error_type=type(e).__name__)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to create user in database: {str(e)}"
            )
        
        if not user.data:
            logger.error("user_creation_failed", email=user_data.email, response=user)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create user - no data returned"
            )
        
        user_id = user.data[0]["id"]
        logger.info("user_created", user_id=user_id, email=user_data.email)
        
        # Create workspace with owner
        workspace = supabase.table("workspaces").insert({
            "name": user_data.workspace_name,
            "address": user_data.address or "",
            "timezone": user_data.timezone or "UTC",
            "contact_email": user_data.contact_email or user_data.email,
            "status": "setup",
            "onboarding_step": "workspace_created",
            "owner_id": user_id,
        }).execute()
        
        if not workspace.data:
            logger.error("workspace_creation_failed", user_id=user_id)
            # Clean up user if workspace creation fails
            supabase.table("users").delete().eq("id", user_id).execute()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create workspace"
            )
        
        workspace_id = workspace.data[0]["id"]
        logger.info("workspace_created", workspace_id=workspace_id, user_id=user_id)
        
        # Update user with workspace_id
        supabase.table("users").update({
            "workspace_id": workspace_id
        }).eq("id", user_id).execute()
        
        # Create tokens
        token_data = {
            "sub": user_id,
            "email": user_data.email,
            "role": UserRole.OWNER.value,
            "workspace_id": workspace_id,
        }
        
        access_token = create_access_token(token_data)
        refresh_token = create_refresh_token(token_data)
        
        logger.info("registration_successful", user_id=user_id, workspace_id=workspace_id)
        return Token(access_token=access_token, refresh_token=refresh_token)
    
    except HTTPException:
        raise
    except ValueError as e:
        # Password validation errors
        logger.warning("password_validation_error", error=str(e), email=user_data.email)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        # Log the full error for debugging
        error_msg = str(e)
        logger.exception("registration_error", error=error_msg, email=user_data.email, error_type=type(e).__name__)
        
        # Check if it's a Supabase error
        if "supabase" in error_msg.lower() or "postgres" in error_msg.lower() or "database" in error_msg.lower():
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database error occurred. Please try again later."
            )
        
        # Generic error
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Registration failed. Please try again."
        )


@router.post("/login", response_model=Token)
async def login(
    credentials: UserLogin,
    supabase: Client = Depends(get_supabase_service)
):
    """Login user"""
    try:
        # Get user
        user_response = supabase.table("users").select("*").eq("email", credentials.email).execute()
        
        if not user_response.data:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials"
            )
        
        user = user_response.data[0]
        
        # Verify password
        if not verify_password(credentials.password, user["password_hash"]):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials"
            )
        
        if not user["is_active"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Account is inactive"
            )
        
        # Create tokens
        token_data = {
            "sub": user["id"],
            "email": user["email"],
            "role": user["role"],
            "workspace_id": user.get("workspace_id"),
        }
        
        access_token = create_access_token(token_data)
        refresh_token = create_refresh_token(token_data)
        
        return Token(access_token=access_token, refresh_token=refresh_token)
    
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("login_error", error=str(e), email=credentials.email)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Login failed"
        )


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: TokenData = Depends(get_current_user),
    supabase: Client = Depends(get_supabase_service)
):
    """Get current user information"""
    try:
        user_response = supabase.table("users").select("*").eq("id", current_user.user_id).execute()
        
        if not user_response.data:
            logger.warning("user_not_found", user_id=current_user.user_id)
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        return UserResponse(**user_response.data[0])
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("get_user_error", user_id=current_user.user_id, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve user information"
        )
