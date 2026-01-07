# app/security.py - Security Module Guide

## Overview

The `security.py` module provides comprehensive security utilities for the Construction AI Landing Page application.

**Purpose:**
- JWT token creation and verification
- Password hashing and verification
- Token expiration handling
- Refresh token support
- Email verification tokens
- Password reset tokens
- Rate limiting
- Security headers
- Validation utilities

---

## Features

✅ **JWT Token Management** - Create and verify tokens
✅ **Password Hashing** - Bcrypt-based password hashing
✅ **Token Types** - Access, refresh, email verification, password reset
✅ **Token Expiration** - Automatic expiration handling
✅ **Rate Limiting** - Simple rate limiter implementation
✅ **Security Headers** - Recommended security headers
✅ **Validation** - Email and password validation
✅ **API Keys** - Generate secure API keys
✅ **Verification Codes** - Generate numeric codes
✅ **Error Handling** - Comprehensive error handling

---

## Password Utilities

### hash_password(password)

Hash a password using bcrypt.

**Parameters:**
- password: Plain text password

**Returns:**
- Hashed password

**Validation:**
- Minimum length: 8 characters (configurable)
- Maximum length: 128 characters (configurable)
- Cannot be empty

**Example:**
```python
from app.security import hash_password, verify_password

# Hash password
hashed = hash_password("MyPassword123!")

# Verify password
is_correct = verify_password("MyPassword123!", hashed)  # True
is_correct = verify_password("WrongPassword", hashed)   # False
```

**Raises:**
- ValueError: If password is empty or invalid length

---

### verify_password(plain_password, hashed_password)

Verify a plain text password against a hashed password.

**Parameters:**
- plain_password: Plain text password
- hashed_password: Hashed password

**Returns:**
- True if password matches, False otherwise

**Example:**
```python
from app.security import hash_password, verify_password

hashed = hash_password("MyPassword123!")
if verify_password("MyPassword123!", hashed):
    print("Password is correct")
```

---

## Token Management

### create_access_token(data, expires_delta, token_type)

Create a JWT access token.

**Parameters:**
- data: Dictionary of data to encode
- expires_delta: Optional custom expiration time
- token_type: Type of token (default: "access")

**Returns:**
- Encoded JWT token

**Default Expiration:**
- From config: ACCESS_TOKEN_EXPIRE_MINUTES (default: 30 minutes)

**Example:**
```python
from app.security import create_access_token
from datetime import timedelta

# Create token with default expiration
token = create_access_token(data={"sub": "user@example.com"})

# Create token with custom expiration
token = create_access_token(
    data={"sub": "user@example.com"},
    expires_delta=timedelta(hours=1)
)
```

**Token Payload:**
```json
{
    "sub": "user@example.com",
    "exp": 1234567890,
    "iat": 1234567800,
    "type": "access"
}
```

---

### verify_token(token, token_type)

Verify and decode a JWT token.

**Parameters:**
- token: JWT token to verify
- token_type: Expected token type (default: "access")

**Returns:**
- Decoded token payload (dictionary)

**Raises:**
- HTTPException (401): If token is invalid, expired, or wrong type

**Example:**
```python
from app.security import verify_token

try:
    payload = verify_token(token)
    user_email = payload.get("sub")
except HTTPException as e:
    print(f"Token verification failed: {e.detail}")
```

**Error Codes:**
- 401 Unauthorized: Token expired, invalid, or wrong type

---

### create_refresh_token(data, expires_delta)

Create a JWT refresh token with longer expiration.

**Parameters:**
- data: Dictionary of data to encode
- expires_delta: Optional custom expiration time (default: 7 days)

**Returns:**
- Encoded JWT refresh token

**Example:**
```python
from app.security import create_refresh_token

refresh_token = create_refresh_token(data={"sub": "user@example.com"})
```

**Use Case:**
- Refresh tokens are used to obtain new access tokens
- Longer expiration than access tokens
- Stored securely (httpOnly cookies)

---

### create_email_verification_token(email)

Create an email verification token.

**Parameters:**
- email: Email address to verify

**Returns:**
- Encoded JWT verification token

**Expiration:**
- 24 hours

**Example:**
```python
from app.security import create_email_verification_token

token = create_email_verification_token("user@example.com")
# Send token in email verification link
```

---

### create_password_reset_token(email)

Create a password reset token.

**Parameters:**
- email: Email address for password reset

**Returns:**
- Encoded JWT reset token

**Expiration:**
- 1 hour

**Example:**
```python
from app.security import create_password_reset_token

token = create_password_reset_token("user@example.com")
# Send token in password reset link
```

---

### verify_email_token(token)

Verify an email verification token.

**Parameters:**
- token: Email verification token

**Returns:**
- Email address from token

**Raises:**
- HTTPException (401): If token is invalid or expired

**Example:**
```python
from app.security import verify_email_token

try:
    email = verify_email_token(token)
    print(f"Email verified: {email}")
except HTTPException as e:
    print(f"Verification failed: {e.detail}")
```

---

### verify_password_reset_token(token)

Verify a password reset token.

**Parameters:**
- token: Password reset token

**Returns:**
- Email address from token

**Raises:**
- HTTPException (401): If token is invalid or expired

**Example:**
```python
from app.security import verify_password_reset_token

try:
    email = verify_password_reset_token(token)
    print(f"Reset token valid for: {email}")
except HTTPException as e:
    print(f"Reset failed: {e.detail}")
```

---

## Authentication Dependencies

### get_current_user(credentials)

FastAPI dependency to get current authenticated user.

**Parameters:**
- credentials: HTTP Bearer credentials (auto-injected)

**Returns:**
- Decoded token payload

**Raises:**
- HTTPException (401): If token is missing or invalid

**Usage in Routes:**
```python
from fastapi import Depends
from app.security import get_current_user

@app.get("/api/me")
async def get_me(current_user = Depends(get_current_user)):
    return {
        "email": current_user.get("sub"),
        "token_type": current_user.get("type")
    }
```

**Client Request:**
```bash
curl -H "Authorization: Bearer <token>" http://localhost:8000/api/me
```

---

### get_current_user_email(current_user)

Get current user's email from token.

**Parameters:**
- current_user: Current user from token (auto-injected)

**Returns:**
- User's email address

**Raises:**
- HTTPException (401): If email not in token

**Usage in Routes:**
```python
from fastapi import Depends
from app.security import get_current_user_email

@app.get("/api/me")
async def get_me(email: str = Depends(get_current_user_email)):
    return {"email": email}
```

---

## Security Utilities

### generate_secure_token(length)

Generate a cryptographically secure random token.

**Parameters:**
- length: Token length in bytes (default: 32)

**Returns:**
- URL-safe random token

**Example:**
```python
from app.security import generate_secure_token

token = generate_secure_token(32)
# Output: "AbCdEfGhIjKlMnOpQrStUvWxYz1234567890"
```

---

### generate_verification_code(length)

Generate a numeric verification code.

**Parameters:**
- length: Code length (default: 6)

**Returns:**
- Numeric code as string

**Example:**
```python
from app.security import generate_verification_code

code = generate_verification_code(6)
# Output: "123456"
```

---

### hash_token(token)

Hash a token for storage.

**Parameters:**
- token: Token to hash

**Returns:**
- SHA256 hashed token

**Example:**
```python
from app.security import hash_token, verify_token_hash

token = "my-secure-token"
hashed = hash_token(token)

# Store hashed token in database
# Later, verify:
if verify_token_hash(token, hashed):
    print("Token is valid")
```

---

### verify_token_hash(token, hashed_token)

Verify a token against its hash.

**Parameters:**
- token: Plain token
- hashed_token: Hashed token

**Returns:**
- True if token matches hash

**Security Note:**
- Uses HMAC compare to prevent timing attacks

---

### generate_api_key(prefix)

Generate an API key with prefix.

**Parameters:**
- prefix: API key prefix (default: "sk")

**Returns:**
- Formatted API key

**Example:**
```python
from app.security import generate_api_key

api_key = generate_api_key("sk")
# Output: "sk_AbCdEfGhIjKlMnOpQrStUvWxYz1234567890"
```

---

## Rate Limiting

### RateLimiter Class

Simple rate limiter for API endpoints.

**Constructor:**
```python
RateLimiter(max_requests=100, window_seconds=60)
```

**Parameters:**
- max_requests: Maximum requests per window (default: 100)
- window_seconds: Time window in seconds (default: 60)

**Methods:**

#### is_allowed(identifier)
Check if request is allowed for identifier.

**Parameters:**
- identifier: Client identifier (IP, user ID, etc)

**Returns:**
- True if request is allowed

**Example:**
```python
from app.security import RateLimiter
from fastapi import Request, HTTPException

limiter = RateLimiter(max_requests=100, window_seconds=60)

@app.get("/api/endpoint")
async def endpoint(request: Request):
    if not limiter.is_allowed(request.client.host):
        raise HTTPException(status_code=429, detail="Too many requests")
    # ... endpoint logic
```

#### get_remaining(identifier)
Get remaining requests for identifier.

**Parameters:**
- identifier: Client identifier

**Returns:**
- Number of remaining requests

**Example:**
```python
remaining = limiter.get_remaining("192.168.1.1")
print(f"Remaining requests: {remaining}")
```

---

## Security Headers

### get_security_headers()

Get recommended security headers.

**Returns:**
- Dictionary of security headers

**Headers Included:**
- X-Content-Type-Options: nosniff
- X-Frame-Options: DENY
- X-XSS-Protection: 1; mode=block
- Strict-Transport-Security: max-age=31536000 (production only when HTTPS is enforced)
- Content-Security-Policy: default-src 'self'
- Referrer-Policy: strict-origin-when-cross-origin

**Example:**
```python
from app.security import get_security_headers

headers = get_security_headers()
# Use in middleware
response.headers.update(headers)
```

---

## Validation Utilities

### validate_email(email)

Validate email format.

**Parameters:**
- email: Email address to validate

**Returns:**
- True if email is valid

**Example:**
```python
from app.security import validate_email

if validate_email("user@example.com"):
    print("Email is valid")
```

---

### validate_password_strength(password)

Validate password strength.

**Requirements:**
- At least 8 characters
- At least one uppercase letter
- At least one lowercase letter
- At least one digit
- At least one special character

**Parameters:**
- password: Password to validate

**Returns:**
- Tuple of (is_valid, message)

**Example:**
```python
from app.security import validate_password_strength

is_valid, message = validate_password_strength("MyPass123!")
if is_valid:
    print("Password is strong")
else:
    print(f"Password error: {message}")
```

**Error Messages:**
- "Password must be at least 8 characters"
- "Password must contain uppercase letter"
- "Password must contain lowercase letter"
- "Password must contain digit"
- "Password must contain special character"

---

## Token Types

| Type | Use Case | Expiration |
|------|----------|-----------|
| access | API authentication | 30 minutes |
| refresh | Get new access token | 7 days |
| email_verify | Email verification | 24 hours |
| password_reset | Password reset | 1 hour |

---

## Complete Authentication Flow

### 1. User Registration

```python
from app.security import hash_password, create_email_verification_token

# Hash password
hashed_password = hash_password(user_password)

# Create email verification token
verification_token = create_email_verification_token(user_email)

# Store user with hashed password
# Send verification email with token
```

### 2. Email Verification

```python
from app.security import verify_email_token

# User clicks link with token
email = verify_email_token(token)

# Mark email as verified
```

### 3. User Login

```python
from app.security import verify_password, create_access_token, create_refresh_token

# Verify password
if verify_password(provided_password, stored_hash):
    # Create tokens
    access_token = create_access_token(data={"sub": user_email})
    refresh_token = create_refresh_token(data={"sub": user_email})
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }
```

### 4. Protected Endpoint

```python
from fastapi import Depends
from app.security import get_current_user_email

@app.get("/api/me")
async def get_me(email: str = Depends(get_current_user_email)):
    return {"email": email}
```

### 5. Password Reset Request

```python
from app.security import create_password_reset_token

# User requests password reset
reset_token = create_password_reset_token(user_email)

# Send reset email with token
```

### 6. Password Reset

```python
from app.security import verify_password_reset_token, hash_password

# User clicks reset link with token
email = verify_password_reset_token(token)

# Hash new password
new_hashed = hash_password(new_password)

# Update user password
```

---

## Configuration

Settings used from `app/config.py`:

| Setting | Default | Description |
|---------|---------|-------------|
| SECRET_KEY | your-secret-key | Secret key for JWT |
| ALGORITHM | HS256 | JWT algorithm |
| ACCESS_TOKEN_EXPIRE_MINUTES | 30 | Token expiration |
| MIN_PASSWORD_LENGTH | 8 | Minimum password length |
| MAX_PASSWORD_LENGTH | 128 | Maximum password length |

---

## Dependencies

**External Libraries:**
- PyJWT: JWT token handling
- passlib: Password hashing
- bcrypt: Bcrypt algorithm

**Installation:**
```bash
pip install pyjwt passlib bcrypt
```

---

## Security Best Practices

### 1. Secret Key
- Generate strong secret key
- Keep it secret (use environment variables)
- Rotate periodically

```bash
# Generate secret key
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

### 2. Token Storage
- Store access tokens in memory
- Store refresh tokens in httpOnly cookies
- Never store in localStorage

### 3. HTTPS
- Always use HTTPS in production
- Use secure cookies (Secure, HttpOnly, SameSite)

### 4. Token Expiration
- Keep access token expiration short (15-30 min)
- Use refresh tokens for longer sessions
- Implement token rotation

### 5. Password Security
- Require strong passwords
- Hash passwords with bcrypt
- Never store plain passwords
- Implement rate limiting on login

### 6. Rate Limiting
- Limit login attempts
- Limit API calls per user
- Implement exponential backoff

---

## Error Handling

All token verification functions raise HTTPException with status 401:

```python
from fastapi import HTTPException

# Token expired
HTTPException(status_code=401, detail="Token has expired")

# Invalid token
HTTPException(status_code=401, detail="Invalid token")

# Wrong token type
HTTPException(status_code=401, detail="Invalid token type...")
```

---

## File Placement

```
app/
├── __init__.py
├── security.py                  # ← This file
├── config.py
├── main.py
├── database.py
├── models/
├── routes/
├── schemas/
├── utils/
├── templates/
└── static/
```

---

## Summary

The `app/security.py` module provides:

✅ **JWT Token Management** - Create and verify tokens
✅ **Password Hashing** - Bcrypt-based hashing
✅ **Token Types** - Access, refresh, email, password reset
✅ **Token Expiration** - Automatic expiration handling
✅ **Authentication Dependencies** - FastAPI integration
✅ **Rate Limiting** - Simple rate limiter
✅ **Security Headers** - Recommended headers
✅ **Validation** - Email and password validation
✅ **API Keys** - Generate secure keys
✅ **Verification Codes** - Generate numeric codes
✅ **Error Handling** - Comprehensive error handling
✅ **Security Best Practices** - Implemented throughout
✅ **Production-ready** - Fully tested and documented

Everything is production-ready and fully documented!
