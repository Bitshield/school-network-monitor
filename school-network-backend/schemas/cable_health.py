from pydantic import BaseModel, Field, field_validator
from datetime import datetime
from typing import Optional
from enum import Enum as PyEnum


class CableHealthStatusEnum(str, PyEnum):
    EXCELLENT = "EXCELLENT"
    GOOD = "GOOD"
    FAIR = "FAIR"
    POOR = "POOR"
    CRITICAL = "CRITICAL"
    UNKNOWN = "UNKNOWN"


class CableTypeEnum(str, PyEnum):
    CAT5 = "CAT5"
    CAT5E = "CAT5E"
    CAT6 = "CAT6"
    CAT6A = "CAT6A"
    CAT7 = "CAT7"
    FIBER_SM = "FIBER_SM"  # Single-mode fiber
    FIBER_MM = "FIBER_MM"  # Multi-mode fiber
    COAX = "COAX"
    UNKNOWN = "UNKNOWN"


class CableHealthCreate(BaseModel):
    """Create cable health record request."""
    link_id: str
    cable_type: Optional[CableTypeEnum] = CableTypeEnum.UNKNOWN
    length: Optional[float] = Field(None, ge=0, description="Cable length in meters")
    signal_strength: Optional[float] = Field(None, ge=-100, le=0, description="Signal strength in dBm")
    signal_quality: Optional[int] = Field(None, ge=0, le=100, description="Signal quality percentage")
    noise_level: Optional[float] = Field(None, ge=-100, le=0, description="Noise level in dBm")
    attenuation: Optional[float] = Field(None, ge=0, description="Attenuation in dB")
    impedance: Optional[float] = Field(None, ge=0, description="Impedance in Ohms")
    pair1_status: Optional[str] = Field(None, max_length=50)
    pair2_status: Optional[str] = Field(None, max_length=50)
    pair3_status: Optional[str] = Field(None, max_length=50)
    pair4_status: Optional[str] = Field(None, max_length=50)
    
    @field_validator('signal_quality')
    @classmethod
    def validate_signal_quality(cls, v):
        if v is not None and not (0 <= v <= 100):
            raise ValueError('Signal quality must be between 0 and 100')
        return v


class CableHealthUpdate(BaseModel):
    """Update cable health record request."""
    cable_type: Optional[CableTypeEnum] = None
    length: Optional[float] = None
    signal_strength: Optional[float] = None
    signal_quality: Optional[int] = None
    noise_level: Optional[float] = None
    attenuation: Optional[float] = None
    impedance: Optional[float] = None
    status: Optional[CableHealthStatusEnum] = None
    pair1_status: Optional[str] = None
    pair2_status: Optional[str] = None
    pair3_status: Optional[str] = None
    pair4_status: Optional[str] = None


class CableHealthResponse(BaseModel):
    """Cable health response."""
    id: str
    link_id: str
    cable_type: CableTypeEnum
    status: CableHealthStatusEnum
    length: Optional[float]
    signal_strength: Optional[float]
    signal_quality: Optional[int]
    noise_level: Optional[float]
    snr: Optional[float]  # Signal-to-Noise Ratio
    attenuation: Optional[float]
    impedance: Optional[float]
    pair1_status: Optional[str]
    pair2_status: Optional[str]
    pair3_status: Optional[str]
    pair4_status: Optional[str]
    bit_error_rate: Optional[float]
    packet_loss_rate: Optional[float]
    test_date: datetime
    next_test_date: Optional[datetime]
    notes: Optional[str]
    created_at: datetime
    updated_at: datetime
    
    model_config = {"from_attributes": True}


class CableHealthDetailResponse(CableHealthResponse):
    """Cable health with link relationship."""
    link: Optional['LinkResponse'] = None


class CableHealthTestRequest(BaseModel):
    """Request to run cable health test."""
    link_id: str
    test_type: str = Field(default="full", pattern=r'^(quick|full|extended)$')
    notes: Optional[str] = Field(None, max_length=500)


class CableHealthTestResult(BaseModel):
    """Result of cable health test."""
    link_id: str
    test_passed: bool
    status: CableHealthStatusEnum
    signal_quality: Optional[int]
    issues_found: list[str] = []
    recommendations: list[str] = []
    test_duration: float  # in seconds
    tested_at: datetime


# Forward reference
from schemas.link import LinkResponse

CableHealthDetailResponse.model_rebuild()