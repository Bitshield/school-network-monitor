from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, Dict, Any
from enum import Enum as PyEnum


class EventTypeEnum(str, PyEnum):
    DEVICE_UP = "DEVICE_UP"
    DEVICE_DOWN = "DEVICE_DOWN"
    DEVICE_DISCOVERED = "DEVICE_DISCOVERED"
    DEVICE_REMOVED = "DEVICE_REMOVED"
    PORT_UP = "PORT_UP"
    PORT_DOWN = "PORT_DOWN"
    LINK_UP = "LINK_UP"
    LINK_DOWN = "LINK_DOWN"
    HIGH_LATENCY = "HIGH_LATENCY"
    HIGH_PACKET_LOSS = "HIGH_PACKET_LOSS"
    BANDWIDTH_THRESHOLD = "BANDWIDTH_THRESHOLD"
    CONFIGURATION_CHANGE = "CONFIGURATION_CHANGE"
    SECURITY_ALERT = "SECURITY_ALERT"
    BACKUP_COMPLETED = "BACKUP_COMPLETED"
    BACKUP_FAILED = "BACKUP_FAILED"
    SCAN_COMPLETED = "SCAN_COMPLETED"
    SCAN_FAILED = "SCAN_FAILED"
    UNKNOWN = "UNKNOWN"


class EventSeverityEnum(str, PyEnum):
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"
    INFO = "INFO"


class EventCreate(BaseModel):
    """Create event request."""
    event_type: EventTypeEnum
    severity: EventSeverityEnum
    device_id: Optional[str] = None
    port_id: Optional[str] = None
    link_id: Optional[str] = None
    message: str = Field(..., min_length=1, max_length=1000)
    details: Optional[Dict[str, Any]] = None
    source: Optional[str] = Field(None, max_length=100, description="Event source system")


class EventUpdate(BaseModel):
    """Update event request."""
    acknowledged: Optional[bool] = None
    acknowledged_by: Optional[str] = None
    notes: Optional[str] = None


class EventResponse(BaseModel):
    """Event response."""
    id: str
    event_type: EventTypeEnum
    severity: EventSeverityEnum
    device_id: Optional[str]
    port_id: Optional[str]
    link_id: Optional[str]
    message: str
    details: Optional[Dict[str, Any]]
    source: Optional[str]
    acknowledged: bool
    acknowledged_by: Optional[str]
    acknowledged_at: Optional[datetime]
    notes: Optional[str]
    created_at: datetime
    updated_at: datetime
    
    model_config = {"from_attributes": True}


class EventDetailResponse(EventResponse):
    """Event with relationships."""
    device: Optional['DeviceResponse'] = None
    port: Optional['PortResponse'] = None
    link: Optional['LinkResponse'] = None


class EventFilterParams(BaseModel):
    """Event filter parameters."""
    event_type: Optional[EventTypeEnum] = None
    severity: Optional[EventSeverityEnum] = None
    device_id: Optional[str] = None
    acknowledged: Optional[bool] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    limit: int = Field(default=100, ge=1, le=1000)
    offset: int = Field(default=0, ge=0)


# Forward references
from schemas.device import DeviceResponse
from schemas.port import PortResponse
from schemas.link import LinkResponse

EventDetailResponse.model_rebuild()