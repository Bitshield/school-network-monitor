from sqlalchemy import Column, String, DateTime, Float, Enum, ForeignKey, Integer
from sqlalchemy.orm import relationship
from database import Base
from datetime import datetime
from enum import Enum as PyEnum


class LinkStatusEnum(str, PyEnum):
    UP = "UP"
    DOWN = "DOWN"
    DEGRADED = "DEGRADED"
    UNKNOWN = "UNKNOWN"


class LinkTypeEnum(str, PyEnum):
    PHYSICAL = "PHYSICAL"
    LOGICAL = "LOGICAL"
    VIRTUAL = "VIRTUAL"
    UNKNOWN = "UNKNOWN"


class Link(Base):
    __tablename__ = "links"

    id = Column(String, primary_key=True)
    
    # Source and target devices
    source_device_id = Column(String, ForeignKey("devices.id", ondelete="CASCADE"), nullable=False, index=True)
    target_device_id = Column(String, ForeignKey("devices.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Port information (optional)
    source_port_id = Column(String, ForeignKey("ports.id", ondelete="SET NULL"), nullable=True)
    target_port_id = Column(String, ForeignKey("ports.id", ondelete="SET NULL"), nullable=True)
    
    # Link type and status
    link_type = Column(Enum(LinkTypeEnum), default=LinkTypeEnum.PHYSICAL)
    status = Column(Enum(LinkStatusEnum), default=LinkStatusEnum.UNKNOWN, index=True)
    
    # Performance metrics
    bandwidth = Column(Integer, nullable=True)  # in Mbps
    speed_mbps = Column(Float, nullable=True)  # Actual speed
    duplex = Column(String(50), nullable=True)  # Full, Half
    utilization = Column(Float, default=0.0)  # 0-100 percentage
    
    # Health metrics
    packet_loss = Column(Float, default=0.0)  # Percentage
    latency = Column(Float, default=0.0)  # in ms
    jitter = Column(Float, default=0.0)  # in ms
    
    # Routing information
    cost = Column(Integer, nullable=True)  # Link cost for routing protocols
    
    # Description
    description = Column(String(500), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_seen = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    source_device = relationship(
        "Device",
        foreign_keys=[source_device_id],
        back_populates="from_links"
    )
    target_device = relationship(
        "Device",
        foreign_keys=[target_device_id],
        back_populates="to_links"
    )
    source_port = relationship(
        "Port",
        foreign_keys=[source_port_id],
        back_populates="source_links"
    )
    target_port = relationship(
        "Port",
        foreign_keys=[target_port_id],
        back_populates="target_links"
    )
    health_metrics = relationship(
        "CableHealthMetrics",
        back_populates="link",
        cascade="all, delete-orphan"
    )
    events = relationship(
        "Event",
        back_populates="link",
        cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<Link {self.source_device_id}->{self.target_device_id}>"