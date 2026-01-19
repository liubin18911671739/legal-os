import time
import json
from typing import Optional, Dict, Any, Callable
from datetime import datetime, timedelta
from functools import wraps
from collections import defaultdict
import hashlib

import jwt
from fastapi import HTTPException, Request, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from passlib.context import CryptContext


# Security configuration
SECRET_KEY = "your-secret-key-change-in-production"  # Load from environment
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7

# Rate limiting configuration
DEFAULT_RATE_LIMIT = 100  # requests per minute
DEFAULT_BURST = 10  # burst size


# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# HTTP Bearer token authentication
security = HTTPBearer()


class TokenData:
    """Token payload data"""
    
    def __init__(
        self,
        user_id: str,
        username: str,
        role: str = "user",
        exp: Optional[int] = None,
        iat: Optional[int] = None
    ):
        self.user_id = user_id
        self.username = username
        self.role = role
        self.exp = exp
        self.iat = iat
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'TokenData':
        """Create TokenData from dictionary
        
        Args:
            data: Dictionary containing token data
            
        Returns:
            TokenData instance
        """
        return cls(
            user_id=data.get("sub"),
            username=data.get("username"),
            role=data.get("role", "user"),
            exp=data.get("exp"),
            iat=data.get("iat")
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert TokenData to dictionary
        
        Returns:
            Dictionary representation
        """
        data = {
            "sub": self.user_id,
            "username": self.username,
            "role": self.role,
        }
        if self.exp:
            data["exp"] = self.exp
        if self.iat:
            data["iat"] = self.iat
        return data


class RateLimiter:
    """Rate limiter using sliding window algorithm"""
    
    def __init__(self, requests_per_minute: int = DEFAULT_RATE_LIMIT):
        """Initialize rate limiter
        
        Args:
            requests_per_minute: Maximum requests per minute
        """
        self.requests_per_minute = requests_per_minute
        self.requests: Dict[str, list] = defaultdict(list)
    
    def is_allowed(
        self,
        identifier: str,
        window_seconds: int = 60
    ) -> tuple[bool, Optional[Dict[str, int]]]:
        """Check if request is allowed
        
        Args:
            identifier: Unique identifier (IP address, user ID, etc.)
            window_seconds: Time window in seconds
            
        Returns:
            Tuple of (allowed, rate_limit_info)
        """
        current_time = time.time()
        
        # Clean old requests
        self.requests[identifier] = [
            req_time for req_time in self.requests[identifier]
            if current_time - req_time < window_seconds
        ]
        
        # Check if limit exceeded
        request_count = len(self.requests[identifier])
        
        rate_info = {
            "limit": self.requests_per_minute,
            "remaining": max(0, self.requests_per_minute - request_count),
            "reset": int(
                self.requests[identifier][0] + window_seconds
                if self.requests[identifier]
                else current_time + window_seconds
            )
        }
        
        if request_count >= self.requests_per_minute:
            return False, rate_info
        
        # Add current request
        self.requests[identifier].append(current_time)
        return True, rate_info
    
    def reset(self, identifier: str):
        """Reset rate limit for identifier
        
        Args:
            identifier: Unique identifier to reset
        """
        if identifier in self.requests:
            del self.requests[identifier]


# Global rate limiter
rate_limiter = RateLimiter()


def hash_password(password: str) -> str:
    """Hash password
    
    Args:
        password: Plain text password
        
    Returns:
        Hashed password
    """
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password
    
    Args:
        plain_password: Plain text password
        hashed_password: Hashed password
        
    Returns:
        True if password matches
    """
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(
    user_id: str,
    username: str,
    role: str = "user",
    expires_delta: Optional[timedelta] = None
) -> str:
    """Create access token
    
    Args:
        user_id: User ID
        username: Username
        role: User role
        expires_delta: Custom expiration time
        
    Returns:
        JWT access token
    """
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    token_data = TokenData(
        user_id=user_id,
        username=username,
        role=role,
        exp=int(expire.timestamp()),
        iat=int(datetime.utcnow().timestamp())
    )
    
    encoded_jwt = jwt.encode(
        token_data.to_dict(),
        SECRET_KEY,
        algorithm=ALGORITHM
    )
    
    return encoded_jwt


def create_refresh_token(user_id: str) -> str:
    """Create refresh token
    
    Args:
        user_id: User ID
        
    Returns:
        JWT refresh token
    """
    expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    
    token_data = {
        "sub": user_id,
        "exp": int(expire.timestamp()),
        "type": "refresh"
    }
    
    encoded_jwt = jwt.encode(
        token_data,
        SECRET_KEY,
        algorithm=ALGORITHM
    )
    
    return encoded_jwt


def decode_token(token: str) -> Optional[TokenData]:
    """Decode and verify token
    
    Args:
        token: JWT token
        
    Returns:
        TokenData if valid, None otherwise
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        
        # Check if refresh token
        if payload.get("type") == "refresh":
            return None
        
        return TokenData.from_dict(payload)
    except jwt.ExpiredSignatureError:
        return None
    except jwt.JWTError:
        return None


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> TokenData:
    """Get current user from token
    
    Args:
        credentials: HTTP Bearer credentials
        
    Returns:
        TokenData
        
    Raises:
        HTTPException: If token is invalid or expired
    """
    token = credentials.credentials
    token_data = decode_token(token)
    
    if token_data is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return token_data


def require_role(*required_roles: str):
    """Decorator to require specific roles
    
    Args:
        *required_roles: Required roles
        
    Returns:
        Dependency function
    """
    async def role_dependency(current_user: TokenData = Depends(get_current_user)):
        if current_user.role not in required_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions",
            )
        return current_user
    
    return role_dependency


async def rate_limit(
    request: Request,
    limit: Optional[int] = None,
    per: str = "minute"
) -> None:
    """Rate limit dependency
    
    Args:
        request: FastAPI request
        limit: Custom limit (uses default if None)
        per: Time period (minute, hour, day)
        
    Raises:
        HTTPException: If rate limit exceeded
    """
    # Get client identifier (IP address)
    client_host = request.client.host if request.client else "unknown"
    
    # Use custom limit or default
    requests_per_minute = limit if limit else rate_limiter.requests_per_minute
    
    # Check rate limit
    allowed, rate_info = rate_limiter.is_allowed(client_host)
    
    if not allowed:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Rate limit exceeded",
            headers={
                "X-RateLimit-Limit": str(rate_info["limit"]),
                "X-RateLimit-Remaining": str(rate_info["remaining"]),
                "X-RateLimit-Reset": str(rate_info["reset"]),
                "Retry-After": str(max(1, rate_info["reset"] - int(time.time()))),
            },
        )


def rate_limit_decorator(
    requests_per_minute: int = DEFAULT_RATE_LIMIT,
    key_func: Optional[Callable] = None
):
    """Decorator to rate limit functions
    
    Args:
        requests_per_minute: Maximum requests per minute
        key_func: Function to generate rate limit key
        
    Returns:
        Decorator function
    """
    limiter = RateLimiter(requests_per_minute)
    
    def decorator(func):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            # Generate key
            if key_func:
                key = key_func(*args, **kwargs)
            else:
                key = "default"
            
            # Check rate limit
            allowed, rate_info = limiter.is_allowed(key)
            
            if not allowed:
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail="Rate limit exceeded",
                    headers={
                        "X-RateLimit-Limit": str(rate_info["limit"]),
                        "X-RateLimit-Remaining": str(rate_info["remaining"]),
                        "X-RateLimit-Reset": str(rate_info["reset"]),
                    },
                )
            
            return await func(*args, **kwargs)
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            # Generate key
            if key_func:
                key = key_func(*args, **kwargs)
            else:
                key = "default"
            
            # Check rate limit
            allowed, rate_info = limiter.is_allowed(key)
            
            if not allowed:
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail="Rate limit exceeded",
                    headers={
                        "X-RateLimit-Limit": str(rate_info["limit"]),
                        "X-RateLimit-Remaining": str(rate_info["remaining"]),
                        "X-RateLimit-Reset": str(rate_info["reset"]),
                    },
                )
            
            return func(*args, **kwargs)
        
        # Return appropriate wrapper
        import asyncio
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator


def validate_file_upload(
    file_size: int,
    allowed_types: list,
    max_size: int = 10 * 1024 * 1024  # 10MB
):
    """Validate file upload
    
    Args:
        file_size: File size in bytes
        allowed_types: List of allowed MIME types
        max_size: Maximum file size
        
    Raises:
        HTTPException: If validation fails
    """
    if file_size > max_size:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File size exceeds maximum allowed size of {max_size} bytes",
        )
    
    # File type validation would be done at the file handler level
    # This function focuses on size validation


def sanitize_input(text: str, max_length: int = 10000) -> str:
    """Sanitize user input
    
    Args:
        text: Input text
        max_length: Maximum allowed length
        
    Returns:
        Sanitized text
        
    Raises:
        HTTPException: If input is too long
    """
    if len(text) > max_length:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Input exceeds maximum allowed length of {max_length}",
        )
    
    # Basic sanitization (can be extended)
    # Remove potential XSS attacks
    import html
    sanitized = html.escape(text)
    
    return sanitized


def generate_api_key() -> str:
    """Generate random API key
    
    Returns:
        API key string
    """
    import secrets
    return secrets.token_urlsafe(32)


def hash_api_key(api_key: str) -> str:
    """Hash API key for storage
    
    Args:
        api_key: API key to hash
        
    Returns:
        Hashed API key
    """
    return hashlib.sha256(api_key.encode()).hexdigest()
