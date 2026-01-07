"""
Construction AI Landing Page - Security Module

This module provides JWT token management, password hashing, and authentication utilities.

Features:
- JWT token creation and verification
- Password hashing and verification
- Token expiration handling
- Refresh token support
- Email verification tokens
- Password reset tokens
- Rate limiting utilities
- CORS security headers
- Security headers middleware

Usage:
    from app.security import create_access_token, verify_token
    
    # Create token
    token = create_access_token(data={"sub": "user@example.com"})
    
    # Verify token
    payload = verify_token(token)
"""

import logging
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any
import secrets
import hashlib
import hmac

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt
from jose.exceptions import JWTError, ExpiredSignatureError
from passlib.context import CryptContext

from app.config import settings

# ============================================================================
# LOGGING
# ============================================================================

logger = logging.getLogger(__name__)

# ============================================================================
# PASSWORD HASHING
# ============================================================================

# Configure password hashing
pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto"
)

# ============================================================================
# SECURITY SCHEMES
# ============================================================================

security = HTTPBearer(
    scheme_name="Bearer",
    description="JWT Bearer token authentication"
)

# ============================================================================
# CONSTANTS
# ============================================================================

TOKEN_TYPE_ACCESS = "access"
TOKEN_TYPE_REFRESH = "refresh"
TOKEN_TYPE_EMAIL_VERIFY = "email_verify"
TOKEN_TYPE_PASSWORD_RESET = "password_reset"

# ============================================================================
# PASSWORD UTILITIES
# ============================================================================

def hash_password(password: str) -> str:
    """
    Hash a password using bcrypt.
    
    Args:
        password: Plain text password
        
    Returns:
        Hashed password
        
    Example:
        >>> hashed = hash_password("mypassword123")
        >>> verify_password("mypassword123", hashed)
        True
    """
    if not password:
        raise ValueError("Password cannot be empty")
    
    if len(password) < settings.MIN_PASSWORD_LENGTH:
        raise ValueError(
            f"Password must be at least {settings.MIN_PASSWORD_LENGTH} characters"
        )
    
    if len(password) > settings.MAX_PASSWORD_LENGTH:
        raise ValueError(
            f"Password must be at most {settings.MAX_PASSWORD_LENGTH} characters"
        )
    
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a plain text password against a hashed password.
    
    Args:
        plain_password: Plain text password
        hashed_password: Hashed password
        
    Returns:
        True if password matches, False otherwise
        
    Example:
        >>> hashed = hash_password("mypassword123")
        >>> verify_password("mypassword123", hashed)
        True
        >>> verify_password("wrongpassword", hashed)
        False
    """
    try:
        return pwd_context.verify(plain_password, hashed_password)
    except Exception as e:
        logger.error(f"Error verifying password: {str(e)}")
        return False

# ============================================================================
# TOKEN UTILITIES
# ============================================================================

def create_access_token(
    data: Dict[str, Any],
    expires_delta: Optional[timedelta] = None,
    token_type: str = TOKEN_TYPE_ACCESS
) -> str:
    """
    Create a JWT access token.
    
    Args:
        data: Data to encode in token
        expires_delta: Custom expiration time
        token_type: Type of token (access, refresh, etc)
        
    Returns:
        Encoded JWT token
        
    Example:
        >>> token = create_access_token(
        ...     data={"sub": "user@example.com"},
        ...     expires_delta=timedelta(hours=1)
        ... )
    """
    to_encode = data.copy()
    
    # Set expiration time
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
    
    to_encode.update({
        "exp": expire,
        "iat": datetime.now(timezone.utc),
        "type": token_type
    })
    
    try:
        encoded_jwt = jwt.encode(
            to_encode,
            settings.SECRET_KEY,
            algorithm=settings.ALGORITHM
        )
        logger.info(f"Created {token_type} token for {data.get('sub', 'unknown')}")
        return encoded_jwt
    except Exception as e:
        logger.error(f"Error creating token: {str(e)}")
        raise


def verify_token(
    token: str,
    token_type: str = TOKEN_TYPE_ACCESS
) -> Dict[str, Any]:
    """
    Verify and decode a JWT token.
    
    Args:
        token: JWT token to verify
        token_type: Expected token type
        
    Returns:
        Decoded token payload
        
    Raises:
        HTTPException: If token is invalid or expired
        
    Example:
        >>> payload = verify_token(token)
        >>> user_email = payload.get("sub")
    """
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )
        
        # Verify token type
        if payload.get("type") != token_type:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Invalid token type. Expected {token_type}, got {payload.get('type')}"
            )
        
        return payload
        
    except ExpiredSignatureError:
        logger.warning(f"Token expired")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired"
        )
    except JWTError as e:
        logger.warning(f"Invalid token: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )
    except Exception as e:
        logger.error(f"Error verifying token: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token verification failed"
        )


def create_refresh_token(
    data: Dict[str, Any],
    expires_delta: Optional[timedelta] = None
) -> str:
    """
    Create a JWT refresh token.
    
    Refresh tokens have longer expiration time than access tokens.
    
    Args:
        data: Data to encode in token
        expires_delta: Custom expiration time (default: 7 days)
        
    Returns:
        Encoded JWT refresh token
        
    Example:
        >>> refresh_token = create_refresh_token(
        ...     data={"sub": "user@example.com"}
        ... )
    """
    if expires_delta is None:
        expires_delta = timedelta(days=7)
    
    return create_access_token(
        data=data,
        expires_delta=expires_delta,
        token_type=TOKEN_TYPE_REFRESH
    )


def create_email_verification_token(email: str) -> str:
    """
    Create an email verification token.
    
    Args:
        email: Email address to verify
        
    Returns:
        Encoded JWT verification token
        
    Example:
        >>> token = create_email_verification_token("user@example.com")
    """
    return create_access_token(
        data={"sub": email},
        expires_delta=timedelta(hours=24),
        token_type=TOKEN_TYPE_EMAIL_VERIFY
    )


def create_password_reset_token(email: str) -> str:
    """
    Create a password reset token.
    
    Args:
        email: Email address for password reset
        
    Returns:
        Encoded JWT reset token
        
    Example:
        >>> token = create_password_reset_token("user@example.com")
    """
    return create_access_token(
        data={"sub": email},
        expires_delta=timedelta(hours=1),
        token_type=TOKEN_TYPE_PASSWORD_RESET
    )


def verify_email_token(token: str) -> str:
    """
    Verify an email verification token.
    
    Args:
        token: Email verification token
        
    Returns:
        Email address from token
        
    Raises:
        HTTPException: If token is invalid
        
    Example:
        >>> email = verify_email_token(token)
    """
    payload = verify_token(token, token_type=TOKEN_TYPE_EMAIL_VERIFY)
    return payload.get("sub")


def verify_password_reset_token(token: str) -> str:
    """
    Verify a password reset token.
    
    Args:
        token: Password reset token
        
    Returns:
        Email address from token
        
    Raises:
        HTTPException: If token is invalid
        
    Example:
        >>> email = verify_password_reset_token(token)
    """
    payload = verify_token(token, token_type=TOKEN_TYPE_PASSWORD_RESET)
    return payload.get("sub")

# ============================================================================
# AUTHENTICATION DEPENDENCIES
# ============================================================================

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> Dict[str, Any]:
    """
    FastAPI dependency to get current authenticated user.
    
    Usage in routes:
        @app.get("/api/me")
        async def get_me(current_user = Depends(get_current_user)):
            return current_user
    
    Args:
        credentials: HTTP Bearer credentials
        
    Returns:
        Decoded token payload
        
    Raises:
        HTTPException: If token is invalid or missing
    """
    token = credentials.credentials
    payload = verify_token(token, token_type=TOKEN_TYPE_ACCESS)
    return payload


async def get_current_user_email(
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> str:
    """
    Get current user's email from token.
    
    Usage in routes:
        @app.get("/api/me")
        async def get_me(email: str = Depends(get_current_user_email)):
            return {"email": email}
    
    Args:
        current_user: Current user from token
        
    Returns:
        User's email address
        
    Raises:
        HTTPException: If email not in token
    """
    email = current_user.get("sub")
    if not email:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email not found in token"
        )
    return email

# ============================================================================
# SECURITY UTILITIES
# ============================================================================

def generate_secure_token(length: int = 32) -> str:
    """
    Generate a cryptographically secure random token.
    
    Args:
        length: Token length in bytes
        
    Returns:
        URL-safe random token
        
    Example:
        >>> token = generate_secure_token()
        >>> len(token) > 0
        True
    """
    return secrets.token_urlsafe(length)


def generate_verification_code(length: int = 6) -> str:
    """
    Generate a numeric verification code.
    
    Args:
        length: Code length
        
    Returns:
        Numeric code as string
        
    Example:
        >>> code = generate_verification_code(6)
        >>> len(code) == 6
        True
        >>> code.isdigit()
        True
    """
    return "".join(str(secrets.randbelow(10)) for _ in range(length))


def hash_token(token: str) -> str:
    """
    Hash a token for storage.
    
    Args:
        token: Token to hash
        
    Returns:
        Hashed token
        
    Example:
        >>> hashed = hash_token(token)
    """
    return hashlib.sha256(token.encode()).hexdigest()


def verify_token_hash(token: str, hashed_token: str) -> bool:
    """
    Verify a token against its hash.
    
    Args:
        token: Plain token
        hashed_token: Hashed token
        
    Returns:
        True if token matches hash
        
    Example:
        >>> hashed = hash_token(token)
        >>> verify_token_hash(token, hashed)
        True
    """
    return hmac.compare_digest(hash_token(token), hashed_token)


def generate_api_key(prefix: str = "sk") -> str:
    """
    Generate an API key with prefix.
    
    Args:
        prefix: API key prefix
        
    Returns:
        Formatted API key
        
    Example:
        >>> key = generate_api_key("sk")
        >>> key.startswith("sk_")
        True
    """
    token = generate_secure_token(32)
    return f"{prefix}_{token}"

# ============================================================================
# RATE LIMITING
# ============================================================================

class RateLimiter:
    """
    Simple rate limiter for API endpoints.
    
    Usage:
        limiter = RateLimiter(max_requests=100, window_seconds=60)
        
        @app.get("/api/endpoint")
        async def endpoint(request: Request):
            if not limiter.is_allowed(request.client.host):
                raise HTTPException(status_code=429)
            # ... endpoint logic
    """
    
    def __init__(self, max_requests: int = 100, window_seconds: int = 60):
        """
        Initialize rate limiter.
        
        Args:
            max_requests: Maximum requests per window
            window_seconds: Time window in seconds
        """
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests: Dict[str, list] = {}
    
    def is_allowed(self, identifier: str) -> bool:
        """
        Check if request is allowed for identifier.
        
        Args:
            identifier: Client identifier (IP, user ID, etc)
            
        Returns:
            True if request is allowed
        """
        now = datetime.now(timezone.utc)
        window_start = now - timedelta(seconds=self.window_seconds)
        
        # Initialize if not exists
        if identifier not in self.requests:
            self.requests[identifier] = []
        
        # Remove old requests outside window
        self.requests[identifier] = [
            req_time for req_time in self.requests[identifier]
            if req_time > window_start
        ]
        
        # Check if limit exceeded
        if len(self.requests[identifier]) >= self.max_requests:
            return False
        
        # Add current request
        self.requests[identifier].append(now)
        return True
    
    def get_remaining(self, identifier: str) -> int:
        """
        Get remaining requests for identifier.
        
        Args:
            identifier: Client identifier
            
        Returns:
            Number of remaining requests
        """
        if identifier not in self.requests:
            return self.max_requests
        
        now = datetime.now(timezone.utc)
        window_start = now - timedelta(seconds=self.window_seconds)
        
        # Count requests in window
        count = len([
            req_time for req_time in self.requests[identifier]
            if req_time > window_start
        ])
        
        return max(0, self.max_requests - count)

# ============================================================================
# SECURITY HEADERS
# ============================================================================

def get_security_headers() -> Dict[str, str]:
    """
    Get recommended security headers.
    
    Returns:
        Dictionary of security headers
        
    Example:
        >>> headers = get_security_headers()
        >>> response.headers.update(headers)
    """
    headers: Dict[str, str] = {
        "X-Content-Type-Options": "nosniff",
        "X-Frame-Options": "DENY",
        "X-XSS-Protection": "1; mode=block",
        "Content-Security-Policy": "default-src 'self'",
        "Referrer-Policy": "strict-origin-when-cross-origin",
    }

    # Only send HSTS when HTTPS is enforced.
    if settings.is_production() and getattr(settings, "HTTPS_REDIRECT", False):
        headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"

    return headers

# ============================================================================
# VALIDATION UTILITIES
# ============================================================================

def validate_email(email: str) -> bool:
    """
    Validate email format.
    
    Args:
        email: Email address to validate
        
    Returns:
        True if email is valid
        
    Example:
        >>> validate_email("user@example.com")
        True
        >>> validate_email("invalid-email")
        False
    """
    import re
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


def validate_password_strength(password: str) -> tuple[bool, str]:
    """
    Validate password strength.
    
    Requirements:
    - At least 8 characters
    - At least one uppercase letter
    - At least one lowercase letter
    - At least one digit
    - At least one special character
    
    Args:
        password: Password to validate
        
    Returns:
        Tuple of (is_valid, message)
        
    Example:
        >>> is_valid, msg = validate_password_strength("MyPass123!")
        >>> is_valid
        True
    """
    import re
    
    if len(password) < 8:
        return False, "Password must be at least 8 characters"
    
    if not re.search(r'[A-Z]', password):
        return False, "Password must contain uppercase letter"
    
    if not re.search(r'[a-z]', password):
        return False, "Password must contain lowercase letter"
    
    if not re.search(r'\d', password):
        return False, "Password must contain digit"
    
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        return False, "Password must contain special character"
    
    return True, "Password is strong"

# ============================================================================
# EXPORT
# ============================================================================

__all__ = [
    # Password utilities
    "hash_password",
    "verify_password",
    
    # Token utilities
    "create_access_token",
    "verify_token",
    "create_refresh_token",
    "create_email_verification_token",
    "create_password_reset_token",
    "verify_email_token",
    "verify_password_reset_token",
    
    # Authentication dependencies
    "get_current_user",
    "get_current_user_email",
    
    # Security utilities
    "generate_secure_token",
    "generate_verification_code",
    "hash_token",
    "verify_token_hash",
    "generate_api_key",
    
    # Rate limiting
    "RateLimiter",
    
    # Security headers
    "get_security_headers",
    
    # Validation
    "validate_email",
    "validate_password_strength",
    
    # Constants
    "TOKEN_TYPE_ACCESS",
    "TOKEN_TYPE_REFRESH",
    "TOKEN_TYPE_EMAIL_VERIFY",
    "TOKEN_TYPE_PASSWORD_RESET",
    
    # Security scheme
    "security",
]
