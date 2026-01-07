"""
Construction AI Landing Page - Authentication Routes

This module provides authentication endpoints for user registration, login, and token management.

Endpoints:
- POST /api/auth/register - Register new user
- POST /api/auth/login - Login user
- POST /api/auth/refresh - Refresh access token
- POST /api/auth/logout - Logout user
- GET /api/auth/me - Get current user info
- POST /api/auth/verify-email - Verify email address
- POST /api/auth/request-password-reset - Request password reset
- POST /api/auth/reset-password - Reset password
- POST /api/auth/change-password - Change password

Authentication:
- JWT Bearer tokens
- Access token: 30 minutes
- Refresh token: 7 days
- Email verification: 24 hours
- Password reset: 1 hour
"""

import logging
from typing import Optional
from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr, Field

from app.database import get_db
from app.config import settings
from app.security import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
    create_email_verification_token,
    create_password_reset_token,
    verify_email_token,
    verify_password_reset_token,
    get_current_user_email,
    validate_email,
    validate_password_strength,
)
from app.models.contractor import Contractor
from app.utils.email import send_email

# ============================================================================
# LOGGING
# ============================================================================

logger = logging.getLogger(__name__)

# ============================================================================
# ROUTER
# ============================================================================

router = APIRouter(
    prefix="/api/auth",
    tags=["authentication"],
    responses={
        401: {"description": "Unauthorized"},
        422: {"description": "Validation error"},
    },
)

# ============================================================================
# SCHEMAS
# ============================================================================

class UserRegister(BaseModel):
    """User registration request schema."""
    
    company_name: str = Field(..., min_length=2, max_length=255)
    contact_name: str = Field(..., min_length=2, max_length=255)
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=128)
    phone: Optional[str] = Field(None, max_length=20)
    company_size: Optional[str] = Field(None, pattern="^(small|medium|large)$")
    
    class Config:
        schema_extra = {
            "example": {
                "company_name": "ABC Construction",
                "contact_name": "John Smith",
                "email": "john@abcconstruction.com",
                "password": "SecurePass123!",
                "phone": "404-555-0123",
                "company_size": "medium"
            }
        }


class UserLogin(BaseModel):
    """User login request schema."""
    
    email: EmailStr
    password: str
    
    class Config:
        schema_extra = {
            "example": {
                "email": "john@abcconstruction.com",
                "password": "SecurePass123!"
            }
        }


class TokenRefresh(BaseModel):
    """Token refresh request schema."""
    
    refresh_token: str = Field(..., description="Refresh token")
    
    class Config:
        schema_extra = {
            "example": {
                "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
            }
        }


class TokenResponse(BaseModel):
    """Token response schema."""
    
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int = Field(default=1800, description="Expiration time in seconds")
    
    class Config:
        schema_extra = {
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "token_type": "bearer",
                "expires_in": 1800
            }
        }


class UserResponse(BaseModel):
    """User response schema."""
    
    id: int
    company_name: str
    contact_name: str
    email: str
    phone: Optional[str]
    company_size: Optional[str]
    email_verified: bool
    created_at: str
    
    class Config:
        from_attributes = True
        schema_extra = {
            "example": {
                "id": 1,
                "company_name": "ABC Construction",
                "contact_name": "John Smith",
                "email": "john@abcconstruction.com",
                "phone": "404-555-0123",
                "company_size": "medium",
                "email_verified": False,
                "created_at": "2026-01-05T10:30:00"
            }
        }


class PasswordReset(BaseModel):
    """Password reset request schema."""
    
    email: EmailStr
    
    class Config:
        schema_extra = {
            "example": {
                "email": "john@abcconstruction.com"
            }
        }


class PasswordResetConfirm(BaseModel):
    """Password reset confirmation schema."""
    
    token: str
    new_password: str = Field(..., min_length=8, max_length=128)
    
    class Config:
        schema_extra = {
            "example": {
                "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "new_password": "NewSecurePass123!"
            }
        }


class PasswordChange(BaseModel):
    """Password change request schema."""
    
    current_password: str
    new_password: str = Field(..., min_length=8, max_length=128)
    
    class Config:
        schema_extra = {
            "example": {
                "current_password": "OldPass123!",
                "new_password": "NewPass123!"
            }
        }


class MessageResponse(BaseModel):
    """Generic message response schema."""
    
    message: str
    
    class Config:
        schema_extra = {
            "example": {
                "message": "Operation successful"
            }
        }

# ============================================================================
# ENDPOINTS
# ============================================================================

@router.post(
    "/register",
    response_model=TokenResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register new user",
    description="Register a new user account with email and password"
)
async def register(
    user_data: UserRegister,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Register a new user account.
    
    **Request Body:**
    - company_name: Company name (2-255 characters)
    - contact_name: Contact person name (2-255 characters)
    - email: Email address (must be unique)
    - password: Password (8-128 characters)
    - phone: Phone number (optional)
    - company_size: Company size - small, medium, or large (optional)
    
    **Response:**
    - access_token: JWT access token (30 minutes)
    - refresh_token: JWT refresh token (7 days)
    - token_type: Token type (always "bearer")
    - expires_in: Access token expiration in seconds
    
    **Errors:**
    - 400: Email already registered
    - 422: Validation error
    """
    logger.info(f"Registration attempt for email: {user_data.email}")
    
    # Validate email format
    if not validate_email(user_data.email):
        logger.warning(f"Invalid email format: {user_data.email}")
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Invalid email format"
        )
    
    # Validate password strength
    is_valid, message = validate_password_strength(user_data.password)
    if not is_valid:
        logger.warning(f"Weak password for {user_data.email}: {message}")
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Password validation failed: {message}"
        )
    
    # Check if email already exists
    existing_user = db.query(Contractor).filter(
        Contractor.email == user_data.email
    ).first()
    
    if existing_user:
        logger.warning(f"Email already registered: {user_data.email}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Hash password
    hashed_password = hash_password(user_data.password)
    
    # Create new contractor
    new_user = Contractor(
        company_name=user_data.company_name,
        contact_name=user_data.contact_name,
        email=user_data.email,
        phone=user_data.phone,
        company_size=user_data.company_size,
        hashed_password=hashed_password,
        email_verified=False,
        conversion_status="lead"
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    logger.info(f"User registered successfully: {user_data.email}")
    
    # Create tokens
    access_token = create_access_token(data={"sub": user_data.email})
    refresh_token = create_refresh_token(data={"sub": user_data.email})
    
    # Send welcome email in background
    if settings.FEATURE_EMAIL_ENABLED:
        verification_token = create_email_verification_token(user_data.email)
        background_tasks.add_task(
            send_email,
            email=user_data.email,
            subject="Welcome to Construction AI",
            template="welcome",
            context={
                "name": user_data.contact_name,
                "verification_link": f"{settings.APP_URL}/verify-email?token={verification_token}"
            }
        )
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
    }


@router.post(
    "/login",
    response_model=TokenResponse,
    status_code=status.HTTP_200_OK,
    summary="Login user",
    description="Login with email and password to get access and refresh tokens"
)
async def login(
    credentials: UserLogin,
    db: Session = Depends(get_db)
):
    """
    Login user with email and password.
    
    **Request Body:**
    - email: Email address
    - password: Password
    
    **Response:**
    - access_token: JWT access token (30 minutes)
    - refresh_token: JWT refresh token (7 days)
    - token_type: Token type (always "bearer")
    - expires_in: Access token expiration in seconds
    
    **Errors:**
    - 401: Invalid email or password
    - 422: Validation error
    """
    logger.info(f"Login attempt for email: {credentials.email}")
    
    # Find user
    user = db.query(Contractor).filter(
        Contractor.email == credentials.email
    ).first()
    
    if not user or not user.hashed_password:
        logger.warning(f"Login failed - user not found: {credentials.email}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
    # Verify password
    if not verify_password(credentials.password, user.hashed_password):
        logger.warning(f"Login failed - invalid password: {credentials.email}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
    logger.info(f"User logged in successfully: {credentials.email}")
    
    # Create tokens
    access_token = create_access_token(data={"sub": credentials.email})
    refresh_token = create_refresh_token(data={"sub": credentials.email})
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
    }


@router.post(
    "/refresh",
    response_model=TokenResponse,
    status_code=status.HTTP_200_OK,
    summary="Refresh access token",
    description="Use refresh token to get a new access token"
)
async def refresh_token(
    token_data: TokenRefresh,
    db: Session = Depends(get_db)
):
    """
    Refresh access token using refresh token.
    
    **Request Body:**
    - refresh_token: Valid refresh token
    
    **Response:**
    - access_token: New JWT access token (30 minutes)
    - refresh_token: New JWT refresh token (7 days)
    - token_type: Token type (always "bearer")
    - expires_in: Access token expiration in seconds
    
    **Errors:**
    - 401: Invalid or expired refresh token
    - 422: Validation error
    """
    logger.info("Token refresh attempt")
    
    try:
        # Verify refresh token
        payload = verify_token(token_data.refresh_token, token_type="refresh")
        email = payload.get("sub")
        
        # Verify user still exists
        user = db.query(Contractor).filter(
            Contractor.email == email
        ).first()
        
        if not user:
            logger.warning(f"Refresh failed - user not found: {email}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found"
            )
        
        logger.info(f"Token refreshed for user: {email}")
        
        # Create new tokens
        new_access_token = create_access_token(data={"sub": email})
        new_refresh_token = create_refresh_token(data={"sub": email})
        
        return {
            "access_token": new_access_token,
            "refresh_token": new_refresh_token,
            "token_type": "bearer",
            "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Token refresh error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )


@router.post(
    "/logout",
    response_model=MessageResponse,
    status_code=status.HTTP_200_OK,
    summary="Logout user",
    description="Logout user (client should discard tokens)"
)
async def logout(
    email: str = Depends(get_current_user_email)
):
    """
    Logout user.
    
    Note: JWT tokens cannot be revoked server-side. Client should:
    1. Discard access token
    2. Discard refresh token
    3. Clear any session data
    
    **Response:**
    - message: Logout confirmation message
    """
    logger.info(f"User logged out: {email}")
    
    return {
        "message": "Logged out successfully. Please discard your tokens."
    }


@router.get(
    "/me",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
    summary="Get current user",
    description="Get current authenticated user information"
)
async def get_me(
    email: str = Depends(get_current_user_email),
    db: Session = Depends(get_db)
):
    """
    Get current user information.
    
    **Response:**
    - id: User ID
    - company_name: Company name
    - contact_name: Contact person name
    - email: Email address
    - phone: Phone number
    - company_size: Company size
    - email_verified: Email verification status
    - created_at: Account creation date
    
    **Errors:**
    - 401: Unauthorized
    - 404: User not found
    """
    logger.info(f"Get user info: {email}")
    
    user = db.query(Contractor).filter(
        Contractor.email == email
    ).first()
    
    if not user:
        logger.warning(f"User not found: {email}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return user


@router.post(
    "/verify-email",
    response_model=MessageResponse,
    status_code=status.HTTP_200_OK,
    summary="Verify email address",
    description="Verify email address using verification token"
)
async def verify_email(
    token: str,
    db: Session = Depends(get_db)
):
    """
    Verify email address using verification token.
    
    **Query Parameters:**
    - token: Email verification token
    
    **Response:**
    - message: Verification confirmation message
    
    **Errors:**
    - 401: Invalid or expired token
    - 404: User not found
    """
    logger.info("Email verification attempt")
    
    try:
        # Verify token
        email = verify_email_token(token)
        
        # Find user
        user = db.query(Contractor).filter(
            Contractor.email == email
        ).first()
        
        if not user:
            logger.warning(f"User not found for email verification: {email}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Mark email as verified
        user.email_verified = True
        db.commit()
        
        logger.info(f"Email verified: {email}")
        
        return {
            "message": "Email verified successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Email verification error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired verification token"
        )


@router.post(
    "/request-password-reset",
    response_model=MessageResponse,
    status_code=status.HTTP_200_OK,
    summary="Request password reset",
    description="Request password reset email"
)
async def request_password_reset(
    password_reset: PasswordReset,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Request password reset email.
    
    **Request Body:**
    - email: Email address
    
    **Response:**
    - message: Confirmation message
    
    **Note:** Returns success even if email not found (security)
    """
    logger.info(f"Password reset request for: {password_reset.email}")
    
    # Find user
    user = db.query(Contractor).filter(
        Contractor.email == password_reset.email
    ).first()
    
    if user and settings.FEATURE_EMAIL_ENABLED:
        # Create reset token
        reset_token = create_password_reset_token(password_reset.email)
        
        # Send reset email in background
        background_tasks.add_task(
            send_email,
            email=password_reset.email,
            subject="Password Reset Request",
            template="password_reset",
            context={
                "name": user.contact_name,
                "reset_link": f"{settings.APP_URL}/reset-password?token={reset_token}"
            }
        )
        
        logger.info(f"Password reset email sent: {password_reset.email}")
    
    # Always return success (security: don't reveal if email exists)
    return {
        "message": "If the email exists, a password reset link has been sent"
    }


@router.post(
    "/reset-password",
    response_model=MessageResponse,
    status_code=status.HTTP_200_OK,
    summary="Reset password",
    description="Reset password using reset token"
)
async def reset_password(
    reset_data: PasswordResetConfirm,
    db: Session = Depends(get_db)
):
    """
    Reset password using reset token.
    
    **Request Body:**
    - token: Password reset token
    - new_password: New password (8-128 characters)
    
    **Response:**
    - message: Confirmation message
    
    **Errors:**
    - 401: Invalid or expired token
    - 404: User not found
    - 422: Validation error
    """
    logger.info("Password reset attempt")
    
    try:
        # Validate new password strength
        is_valid, message = validate_password_strength(reset_data.new_password)
        if not is_valid:
            logger.warning(f"Weak password in reset: {message}")
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Password validation failed: {message}"
            )
        
        # Verify token
        email = verify_password_reset_token(reset_data.token)
        
        # Find user
        user = db.query(Contractor).filter(
            Contractor.email == email
        ).first()
        
        if not user:
            logger.warning(f"User not found for password reset: {email}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Hash new password
        hashed_password = hash_password(reset_data.new_password)
        
        # Update password
        user.hashed_password = hashed_password
        db.commit()
        
        logger.info(f"Password reset successful: {email}")
        
        return {
            "message": "Password reset successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Password reset error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired reset token"
        )


@router.post(
    "/change-password",
    response_model=MessageResponse,
    status_code=status.HTTP_200_OK,
    summary="Change password",
    description="Change password for authenticated user"
)
async def change_password(
    password_change: PasswordChange,
    email: str = Depends(get_current_user_email),
    db: Session = Depends(get_db)
):
    """
    Change password for authenticated user.
    
    **Request Body:**
    - current_password: Current password
    - new_password: New password (8-128 characters)
    
    **Response:**
    - message: Confirmation message
    
    **Errors:**
    - 401: Invalid current password
    - 404: User not found
    - 422: Validation error
    """
    logger.info(f"Password change request for: {email}")
    
    # Find user
    user = db.query(Contractor).filter(
        Contractor.email == email
    ).first()
    
    if not user:
        logger.warning(f"User not found for password change: {email}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Verify current password
    if not verify_password(password_change.current_password, user.hashed_password):
        logger.warning(f"Invalid current password: {email}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid current password"
        )
    
    # Validate new password strength
    is_valid, message = validate_password_strength(password_change.new_password)
    if not is_valid:
        logger.warning(f"Weak password in change: {message}")
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Password validation failed: {message}"
        )
    
    # Hash new password
    hashed_password = hash_password(password_change.new_password)
    
    # Update password
    user.hashed_password = hashed_password
    db.commit()
    
    logger.info(f"Password changed successfully: {email}")
    
    return {
        "message": "Password changed successfully"
    }

# ============================================================================
# EXPORT
# ============================================================================

__all__ = ["router"]
