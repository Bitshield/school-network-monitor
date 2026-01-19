from sqlalchemy import String, Integer, DateTime, Float, Enum as SQLEnum, ForeignKey
from sqlalchemy.orm import relationship, Mapped, mapped_column
from database import Base
from datetime import datetime
from enum import Enum as PyEnum
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from models.device import Device


class LinkTypeEnum(str, PyEnum):
    PHYSICAL = "PHYSICAL"
    LOGICAL = "LOGICAL"
    VIRTUAL = "VIRTUAL"


class LinkStatusEnum(str, PyEnum):
    UP = "UP"
    DOWN = "DOWN"
    DEGRADED = "DEGRADED"
    UNKNOWN = "UNKNOWN"


class Link(Base):
    __tablename__ = "links"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    
    # Source and target devices
    source_device_id: Mapped[str] = mapped_column(String, ForeignKey("devices.id", ondelete="CASCADE"), nullable=False, index=True)
    target_device_id: Mapped[str] = mapped_column(String, ForeignKey("devices.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Port information (optional)
    source_port_id: Mapped[Optional[str]] = mapped_column(String, ForeignKey("ports.id", ondelete="SET NULL"), nullable=True)
    target_port_id: Mapped[Optional[str]] = mapped_column(String, ForeignKey("ports.id", ondelete="SET NULL"), nullable=True)
    
    # Link type and status
    link_type: Mapped[LinkTypeEnum] = mapped_column(SQLEnum(LinkTypeEnum), default=LinkTypeEnum.PHYSICAL)
    status: Mapped[LinkStatusEnum] = mapped_column(SQLEnum(LinkStatusEnum), default=LinkStatusEnum.UNKNOWN, index=True)
    
    # Performance metrics
    bandwidth: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)  # in Mbps
    speed_mbps: Mapped[Optional[float]] = mapped_column(Float, nullable=True)  # actual speed
    duplex: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)  # Full, Half, etc.
    utilization: Mapped[float] = mapped_column(Float, default=0.0)  # in link percentage
    
    # Health metrics
    packet_loss: Mapped[float] = mapped_column(Float, default=0.0)  # Percentage
    latency: Mapped[float] = mapped_column(Float, default=0.0)  # in ms
    jitter: Mapped[float] = mapped_column(Float, default=0.0)  # in ms
    
    # Routing information
    cost: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)  # Link cost for routing protocols
    
    # Description
    description: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_seen: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    source_device: Mapped["Device"] = relationship(
        "Device",
        foreign_keys=[source_device_id],
        back_populates="from_links"
    )
    target_device: Mapped["Device"] = relationship(
        "Device",
        foreign_keys=[target_device_id],
        back_populates="to_links"
    )
    source_port: Mapped[Optional["Port"]] = relationship( # type: ignore
        "Port",
        foreign_keys=[source_port_id],
        back_populates="outgoing_links"
    )
    target_port: Mapped[Optional["Port"]] = relationship( # type: ignore
        "Port",
        foreign_keys=[target_port_id],
        back_populates="incoming_links"
    )

    def __repr__(self):
        return f"<Link {self.id} ({self.source_device_id} -> {self.target_device_id})>"