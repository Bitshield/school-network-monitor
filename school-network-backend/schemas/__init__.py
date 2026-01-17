"""
Pydantic schemas for API request/response validation.
"""

from schemas.device import (
    DeviceTypeEnum,
    DeviceStatusEnum,
    DeviceCreate,
    DeviceUpdate,
    DeviceResponse,
    DeviceDetailResponse,
)

from schemas.port import (
    PortTypeEnum,
    PortStatusEnum,
    PortSpeedEnum,
    PortCreate,
    PortUpdate,
    PortResponse,
    PortDetailResponse,
)

from schemas.link import (
    LinkTypeEnum,
    LinkStatusEnum,
    LinkCreate,
    LinkUpdate,
    LinkResponse,
    LinkDetailResponse,
)

from schemas.event import (
    EventTypeEnum,
    EventSeverityEnum,
    EventCreate,
    EventUpdate,
    EventResponse,
    EventDetailResponse,
    EventFilterParams,
)

from schemas.cable_health import (
    CableHealthStatusEnum,
    CableTypeEnum,
    CableHealthCreate,
    CableHealthUpdate,
    CableHealthResponse,
    CableHealthDetailResponse,
    CableHealthTestRequest,
    CableHealthTestResult,
)

__all__ = [
    # Device
    "DeviceTypeEnum",
    "DeviceStatusEnum",
    "DeviceCreate",
    "DeviceUpdate",
    "DeviceResponse",
    "DeviceDetailResponse",
    # Port
    "PortTypeEnum",
    "PortStatusEnum",
    "PortSpeedEnum",
    "PortCreate",
    "PortUpdate",
    "PortResponse",
    "PortDetailResponse",
    # Link
    "LinkTypeEnum",
    "LinkStatusEnum",
    "LinkCreate",
    "LinkUpdate",
    "LinkResponse",
    "LinkDetailResponse",
    # Event
    "EventTypeEnum",
    "EventSeverityEnum",
    "EventCreate",
    "EventUpdate",
    "EventResponse",
    "EventDetailResponse",
    "EventFilterParams",
    # Cable Health
    "CableHealthStatusEnum",
    "CableTypeEnum",
    "CableHealthCreate",
    "CableHealthUpdate",
    "CableHealthResponse",
    "CableHealthDetailResponse",
    "CableHealthTestRequest",
    "CableHealthTestResult",
]