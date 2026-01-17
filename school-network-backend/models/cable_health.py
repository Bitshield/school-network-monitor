from sqlalchemy import Column, String, DateTime, Float, ForeignKey, Integer, Enum
from sqlalchemy.orm import relationship
from database import Base
from datetime import datetime
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
    FIBER_SM = "FIBER_SM"
    FIBER_MM = "FIBER_MM"
    COAX = "COAX"
    UNKNOWN = "UNKNOWN"


class CableHealthMetrics(Base):
    __tablename__ = "cable_health_metrics"

    id = Column(String, primary_key=True)
    link_id = Column(String, ForeignKey("links.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Cable information
    cable_type = Column(Enum(CableTypeEnum), default=CableTypeEnum.UNKNOWN)
    status = Column(Enum(CableHealthStatusEnum), default=CableHealthStatusEnum.UNKNOWN)
    length = Column(Float, nullable=True)  # Cable length in meters
    
    # Signal metrics
    signal_strength = Column(Float, nullable=True)  # in dBm
    signal_quality = Column(Integer, nullable=True)  # 0-100
    noise_level = Column(Float, nullable=True)  # in dBm
    snr = Column(Float, nullable=True)  # Signal-to-Noise Ratio
    attenuation = Column(Float, nullable=True)  # in dB
    impedance = Column(Float, nullable=True)  # in Ohms
    
    # Performance metrics
    latency_ms = Column(Float, nullable=True)
    packet_loss_percent = Column(Float, default=0.0)
    jitter_ms = Column(Float, nullable=True)
    bit_error_rate = Column(Float, nullable=True)
    
    # Error counters
    error_count = Column(Integer, default=0)
    discard_count = Column(Integer, default=0)
    crc_errors = Column(Integer, default=0)
    
    # Cable pair status (for twisted pair cables)
    pair1_status = Column(String(50), nullable=True)
    pair2_status = Column(String(50), nullable=True)
    pair3_status = Column(String(50), nullable=True)
    pair4_status = Column(String(50), nullable=True)
    
    # Health score
    health_score = Column(Float, default=100.0)  # 0-100
    
    # Testing info
    test_date = Column(DateTime, default=datetime.utcnow)
    next_test_date = Column(DateTime, nullable=True)
    notes = Column(String(1000), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    measured_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    link = relationship("Link", back_populates="health_metrics")

    def __repr__(self):
        return f"<CableHealthMetrics {self.link_id}:{self.status}>"