"""
API dependencies - Shared dependencies for API endpoints.
"""

from typing import Generator, Optional, Dict, Any
from fastapi import Depends, HTTPException, status, Header
from sqlalchemy.ext.asyncio import AsyncSession

from database import async_session
from core.security import get_current_user, get_current_active_user
from core.exceptions import raise_unauthorized
from config import settings


async def get_db() -> Generator[AsyncSession, None, None]: # type: ignore
    """
    Dependency to get database session.
    
    Yields:
        AsyncSession: Database session
        
    Usage:
        @app.get("/items")
        async def get_items(db: AsyncSession = Depends(get_db)):
            ...
    """
    async with async_session() as session:
        try:
            yield session # type: ignore
            await session.commit()
        except Exception as e:
            await session.rollback()
            raise
        finally:
            await session.close()


async def get_current_user_optional(
    authorization: Optional[str] = Header(None)
) -> Optional[Dict[str, Any]]:
    """
    Get current user if token is provided, otherwise return None.
    
    Args:
        authorization: Authorization header
        
    Returns:
        User data or None
        
    Usage:
        @app.get("/items")
        async def get_items(user: Optional[Dict] = Depends(get_current_user_optional)):
            if user:
                # Authenticated request
            else:
                # Anonymous request
    """
    if not authorization:
        return None
    
    try:
        # Extract token from "Bearer <token>"
        if not authorization.startswith("Bearer "):
            return None
        
        token = authorization.split(" ")[1]
        
        from core.security import TokenManager
        payload = TokenManager.decode_token(token)
        return payload
    except Exception:
        return None


class Pagination:
    """
    Pagination dependency for list endpoints.
    
    Usage:
        @app.get("/items")
        async def get_items(pagination: Pagination = Depends()):
            skip = pagination.skip
            limit = pagination.limit
    """
    
    def __init__(
        self,
        page: int = 1,
        page_size: int = settings.DEFAULT_PAGE_SIZE
    ):
        """
        Initialize pagination.
        
        Args:
            page: Page number (1-indexed)
            page_size: Number of items per page
        """
        self.page = max(1, page)
        self.page_size = min(max(1, page_size), settings.MAX_PAGE_SIZE)
        self.skip = (self.page - 1) * self.page_size
        self.limit = self.page_size
    
    @property
    def offset(self) -> int:
        """Get offset for database query."""
        return self.skip


class FilterParams:
    """
    Common filter parameters for list endpoints.
    
    Usage:
        @app.get("/devices")
        async def get_devices(filters: FilterParams = Depends()):
            search = filters.search
            status = filters.status
    """
    
    def __init__(
        self,
        search: Optional[str] = None,
        status: Optional[str] = None,
        device_type: Optional[str] = None,
        sort_by: Optional[str] = None,
        sort_order: str = "asc"
    ):
        """
        Initialize filter parameters.
        
        Args:
            search: Search term
            status: Filter by status
            device_type: Filter by device type
            sort_by: Field to sort by
            sort_order: Sort order (asc or desc)
        """
        self.search = search
        self.status = status
        self.device_type = device_type
        self.sort_by = sort_by
        self.sort_order = sort_order.lower() if sort_order else "asc"


async def verify_api_key(
    x_api_key: Optional[str] = Header(None, alias="X-API-Key")
) -> bool:
    """
    Verify API key for endpoints that support both JWT and API key auth.
    
    Args:
        x_api_key: API key from header
        
    Returns:
        True if valid API key
        
    Raises:
        HTTPException: If API key is invalid
        
    Usage:
        @app.get("/items")
        async def get_items(
            api_key_valid: bool = Depends(verify_api_key),
            user: Optional[Dict] = Depends(get_current_user_optional)
        ):
            if not api_key_valid and not user:
                raise HTTPException(401, "Authentication required")
    """
    if not x_api_key:
        return False
    
    # TODO: Implement API key validation against database
    # For now, compare with a simple key from settings
    # In production, hash and store API keys in database
    
    # Example implementation:
    # from core.security import APIKeyManager
    # if APIKeyManager.verify_api_key(x_api_key, stored_hash):
    #     return True
    
    return False


def require_permissions(*permissions: str):
    """
    Dependency to require specific permissions.
    
    Args:
        permissions: Required permission names
        
    Returns:
        Dependency function
        
    Usage:
        @app.delete("/admin/users/{user_id}")
        async def delete_user(
            user_id: str,
            current_user: Dict = Depends(require_permissions("admin", "delete_users"))
        ):
            ...
    """
    async def permission_checker(
        current_user: Dict = Depends(get_current_active_user)
    ) -> Dict:
        """Check if user has required permissions."""
        user_permissions = current_user.get("permissions", [])
        
        for permission in permissions:
            if permission not in user_permissions:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Permission denied: {permission} required"
                )
        
        return current_user
    
    return permission_checker


class RateLimiter:
    """
    Rate limiting dependency.
    
    Usage:
        rate_limiter = RateLimiter(max_requests=10, window_seconds=60)
        
        @app.get("/items")
        async def get_items(
            limiter: None = Depends(rate_limiter)
        ):
            ...
    """
    
    def __init__(self, max_requests: int = 60, window_seconds: int = 60):
        """
        Initialize rate limiter.
        
        Args:
            max_requests: Maximum requests allowed
            window_seconds: Time window in seconds
        """
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests: Dict[str, list] = {}
    
    async def __call__(self, request) -> None:
        """
        Check rate limit for request.
        
        Args:
            request: FastAPI request object
            
        Raises:
            HTTPException: If rate limit exceeded
        """
        from datetime import datetime, timedelta
        
        # Get client IP
        client_ip = request.client.host
        
        # Get current time
        now = datetime.utcnow()
        
        # Initialize client history if not exists
        if client_ip not in self.requests:
            self.requests[client_ip] = []
        
        # Remove old requests outside the window
        cutoff_time = now - timedelta(seconds=self.window_seconds)
        self.requests[client_ip] = [
            req_time for req_time in self.requests[client_ip]
            if req_time > cutoff_time
        ]
        
        # Check if limit exceeded
        if len(self.requests[client_ip]) >= self.max_requests:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Rate limit exceeded. Max {self.max_requests} requests per {self.window_seconds} seconds."
            )
        
        # Add current request
        self.requests[client_ip].append(now)


# Create commonly used rate limiters
standard_rate_limiter = RateLimiter(
    max_requests=settings.RATE_LIMIT_PER_MINUTE,
    window_seconds=60
)

strict_rate_limiter = RateLimiter(
    max_requests=10,
    window_seconds=60
)


async def get_user_or_none(
    current_user: Optional[Dict] = Depends(get_current_user_optional)
) -> Optional[Dict]:
    """
    Get current user or None for public endpoints.
    
    Returns:
        User data or None
    """
    return current_user


async def require_admin(
    current_user: Dict = Depends(get_current_active_user)
) -> Dict:
    """
    Require admin role.
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        User data if admin
        
    Raises:
        HTTPException: If user is not admin
    """
    if not current_user.get("is_admin", False):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required"
        )
    return current_user


class ServiceDependency:
    """
    Dependency for injecting services.
    
    Usage:
        from services.device import DeviceService
        
        get_device_service = ServiceDependency(DeviceService)
        
        @app.get("/devices")
        async def get_devices(
            device_service: DeviceService = Depends(get_device_service)
        ):
            devices = await device_service.get_all()
    """
    
    def __init__(self, service_class):
        """
        Initialize service dependency.
        
        Args:
            service_class: Service class to instantiate
        """
        self.service_class = service_class
    
    async def __call__(self, db: AsyncSession = Depends(get_db)):
        """
        Create service instance.
        
        Args:
            db: Database session
            
        Returns:
            Service instance
        """
        return self.service_class(db)