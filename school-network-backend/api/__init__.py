"""
API package - REST API endpoints for the application.

This package contains all API endpoints organized by version.
Version 1 (v1) is the current stable API version.

Structure:
    api/
        __init__.py         - This file
        deps.py            - Shared dependencies
        v1/                - Version 1 API
            __init__.py
            router.py      - Main router aggregating all v1 endpoints
            devices.py     - Device management endpoints
            ports.py       - Port management endpoints
            links.py       - Link management endpoints
            events.py      - Event management endpoints
            monitoring.py  - Monitoring endpoints
            discovery.py   - Network discovery endpoints
            health.py      - Health check endpoints
            
Usage:
    from api.v1.router import api_router
    app.include_router(api_router, prefix="/api/v1")
"""

from api.deps import (
    get_db,
    get_current_user_optional,
    get_user_or_none,
    require_admin,
    Pagination,
    FilterParams,
    RateLimiter,
    standard_rate_limiter,
    strict_rate_limiter,
    verify_api_key,
    require_permissions,
    ServiceDependency,
)

__all__ = [
    "get_db",
    "get_current_user_optional",
    "get_user_or_none",
    "require_admin",
    "Pagination",
    "FilterParams",
    "RateLimiter",
    "standard_rate_limiter",
    "strict_rate_limiter",
    "verify_api_key",
    "require_permissions",
    "ServiceDependency",
]

__version__ = "1.0.0"