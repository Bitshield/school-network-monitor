"""
Main API router that aggregates all v1 endpoints.
"""

from fastapi import APIRouter
from api.v1 import (
    devices,
    ports,
    links,
    events,
    cable_health,
    monitoring,
    discovery,
    snmp,
    statistics,
    validation,
)

# Create main API router
api_router = APIRouter()



# Include all endpoint routers
api_router.include_router(
    devices.router,
    prefix="/devices",
    tags=["Devices"]
)


api_router.include_router(
    ports.router,
    prefix="/ports",
    tags=["Ports"]
)

api_router.include_router(
    links.router,
    prefix="/links",
    tags=["Links"]
)

api_router.include_router(
    events.router,
    prefix="/events",
    tags=["Events"]
)

api_router.include_router(
    cable_health.router,
    prefix="/cable-health",
    tags=["Cable Health"]
)

api_router.include_router(
    monitoring.router,
    prefix="/monitoring",
    tags=["Monitoring"]
)

api_router.include_router(
    discovery.router,
    prefix="/discovery",
    tags=["Network Discovery"]
)

api_router.include_router(
    snmp.router,
    prefix="/snmp",
    tags=["SNMP"]
)

api_router.include_router(
    statistics.router,
    prefix="/statistics",
    tags=["Statistics"]
)

api_router.include_router(
    validation.router,
    prefix="/validation",
    tags=["Validation"]
)