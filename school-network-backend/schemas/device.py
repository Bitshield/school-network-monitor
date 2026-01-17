from pydantic import BaseModel, Field, field_validator
from datetime import datetime
from typing import Optional, List
from enum import Enum as PyEnum


class DeviceTypeEnum(str, PyEnum):
    ROUTER = "ROUTER"
    SWITCH = "SWITCH"
    SERVER = "SERVER"
    PC = "PC"
    AP = "AP"
    PRINTER = "PRINTER"
    CAMERA = "CAMERA"
    UNKNOWN = "UNKNOWN"


class DeviceStatusEnum(str, PyEnum):
    UP = "UP"
    DOWN = "DOWN"
    UNREACHABLE = "UNREACHABLE"
    UNKNOWN = "UNKNOWN"


class DeviceCreate(BaseModel):
    """Create device request."""
    name: str = Field(..., min_length=1, max_length=255)
    device_type: DeviceTypeEnum
    ip: Optional[str] = Field(None, pattern=r'^(\d{1,3}\.){3}\d{1,3}$')  # Changed from regex to pattern
    mac: Optional[str] = Field(None, pattern=r'^([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})$')  # Changed from regex to pattern
    hostname: Optional[str] = None
    location: Optional[str] = None
    description: Optional[str] = None
    vlan_id: Optional[int] = None
    snmp_enabled: bool = False
    snmp_community: Optional[str] = None
    position_x: Optional[float] = None
    position_y: Optional[float] = None

    @field_validator('ip')
    @classmethod  # Added classmethod decorator
    def validate_ip(cls, v):
        if v:
            parts = v.split('.')
            for part in parts:
                if not 0 <= int(part) <= 255:
                    raise ValueError('Invalid IP address')
        return v


class DeviceUpdate(BaseModel):
    """Update device request."""
    name: Optional[str] = None
    device_type: Optional[DeviceTypeEnum] = None
    ip: Optional[str] = None
    location: Optional[str] = None
    description: Optional[str] = None
    status: Optional[DeviceStatusEnum] = None
    position_x: Optional[float] = None
    position_y: Optional[float] = None


class DeviceResponse(BaseModel):
    """Device response."""
    id: str
    name: str
    device_type: DeviceTypeEnum
    ip: Optional[str]
    mac: Optional[str]
    hostname: Optional[str]
    location: Optional[str]
    description: Optional[str]
    status: DeviceStatusEnum
    last_seen: datetime
    is_monitored: bool
    vlan_id: Optional[int]
    snmp_enabled: bool
    position_x: Optional[float]
    position_y: Optional[float]
    created_at: datetime
    updated_at: datetime
    
    model_config = {"from_attributes": True}  # Pydantic v2 style


class DeviceDetailResponse(DeviceResponse):
    """Device with relationships."""
    ports: List['PortResponse'] = []
    from_links: List['LinkResponse'] = []
    to_links: List['LinkResponse'] = []


# Forward references
from schemas.link import LinkResponse # type: ignore
from schemas.port import PortResponse # type: ignore

DeviceDetailResponse.model_rebuild()