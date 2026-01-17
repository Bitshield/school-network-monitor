from pydantic import BaseModel, Field, field_validator
from datetime import datetime
from typing import Optional
from enum import Enum as PyEnum


class LinkTypeEnum(str, PyEnum):
    PHYSICAL = "PHYSICAL"
    LOGICAL = "LOGICAL"
    VIRTUAL = "VIRTUAL"
    UNKNOWN = "UNKNOWN"


class LinkStatusEnum(str, PyEnum):
    UP = "UP"
    DOWN = "DOWN"
    DEGRADED = "DEGRADED"
    UNKNOWN = "UNKNOWN"


class LinkCreate(BaseModel):
    """Create link request."""
    source_device_id: str
    target_device_id: str
    source_port_id: Optional[str] = None
    target_port_id: Optional[str] = None
    link_type: LinkTypeEnum = LinkTypeEnum.PHYSICAL
    bandwidth: Optional[int] = Field(None, ge=0, description="Bandwidth in Mbps")
    latency: Optional[float] = Field(None, ge=0, description="Latency in ms")
    description: Optional[str] = Field(None, max_length=500)
    cost: Optional[int] = Field(None, ge=1, le=65535, description="Link cost for routing")
    
    @field_validator('source_device_id', 'target_device_id')
    @classmethod
    def validate_devices_different(cls, v, info):
        if 'source_device_id' in info.data and v == info.data.get('source_device_id'):
            if info.field_name == 'target_device_id':
                raise ValueError('Source and target devices must be different')
        return v


class LinkUpdate(BaseModel):
    """Update link request."""
    link_type: Optional[LinkTypeEnum] = None
    bandwidth: Optional[int] = None
    latency: Optional[float] = None
    description: Optional[str] = None
    status: Optional[LinkStatusEnum] = None
    cost: Optional[int] = None


class LinkResponse(BaseModel):
    """Link response."""
    id: str
    source_device_id: str
    target_device_id: str
    source_port_id: Optional[str]
    target_port_id: Optional[str]
    link_type: LinkTypeEnum
    status: LinkStatusEnum
    bandwidth: Optional[int]
    latency: Optional[float]
    packet_loss: Optional[float]
    utilization: Optional[float]
    description: Optional[str]
    cost: Optional[int]
    last_seen: datetime
    created_at: datetime
    updated_at: datetime
    
    model_config = {"from_attributes": True}


class LinkDetailResponse(LinkResponse):
    """Link with device relationships."""
    source_device: Optional['DeviceResponse'] = None
    target_device: Optional['DeviceResponse'] = None
    source_port: Optional['PortResponse'] = None
    target_port: Optional['PortResponse'] = None


# Forward references
from schemas.device import DeviceResponse
from schemas.port import PortResponse

LinkDetailResponse.model_rebuild()