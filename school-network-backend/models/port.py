from sqlalchemy import Column, String, Integer, DateTime, Float, Boolean, Enum as SQLEnum, ForeignKey
from sqlalchemy.orm import relationship, Mapped, mapped_column
from database import Base
from datetime import datetime
from enum import Enum as PyEnum
from typing import Optional, List, TYPE_CHECKING

if TYPE_CHECKING:
    from models.device import Device
    from models.link import Link
    from models.event import Event


class PortStatusEnum(str, PyEnum):
    UP = "UP"
    DOWN = "DOWN"
    DISABLED = "DISABLED"
    ERROR = "ERROR"
    UNKNOWN = "UNKNOWN"
    TESTING = "TESTING"


class PortTypeEnum(str, PyEnum):
    ETHERNET = "ETHERNET"
    FIBER = "FIBER"
    SFP = "SFP"
    SFP_PLUS = "SFP+"
    QSFP = "QSFP"
    QSFP28 = "QSFP28"
    VIRTUAL = "VIRTUAL"
    LOOPBACK = "LOOPBACK"
    UNKNOWN = "UNKNOWN"


class Port(Base):
    __tablename__ = "ports"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    device_id: Mapped[str] = mapped_column(String, ForeignKey("devices.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Port identification
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    port_number: Mapped[int] = mapped_column(Integer, nullable=False)
    port_name: Mapped[str] = mapped_column(String(50), nullable=False)
    port_type: Mapped[PortTypeEnum] = mapped_column(SQLEnum(PortTypeEnum), default=PortTypeEnum.ETHERNET)
    
    # Port status
    status: Mapped[PortStatusEnum] = mapped_column(SQLEnum(PortStatusEnum), default=PortStatusEnum.UNKNOWN, index=True)
    is_up: Mapped[bool] = mapped_column(Boolean, default=False)
    
    # Port configuration
    speed_mbps: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    max_speed_mbps: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    mtu: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    duplex: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    
    # VLAN configuration
    vlan_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    is_trunk: Mapped[bool] = mapped_column(Boolean, default=False)
    allowed_vlans: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    native_vlan: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    
    # MAC address
    mac_address: Mapped[Optional[str]] = mapped_column(String(17), nullable=True)
    
    # Traffic statistics
    rx_bytes: Mapped[int] = mapped_column(Integer, default=0)
    rx_packets: Mapped[int] = mapped_column(Integer, default=0)
    rx_errors: Mapped[int] = mapped_column(Integer, default=0)
    rx_dropped: Mapped[int] = mapped_column(Integer, default=0)
    
    tx_bytes: Mapped[int] = mapped_column(Integer, default=0)
    tx_packets: Mapped[int] = mapped_column(Integer, default=0)
    tx_errors: Mapped[int] = mapped_column(Integer, default=0)
    tx_dropped: Mapped[int] = mapped_column(Integer, default=0)
    
    # SNMP counters
    in_octets: Mapped[float] = mapped_column(Float, default=0.0)
    in_discards: Mapped[int] = mapped_column(Integer, default=0)
    out_octets: Mapped[float] = mapped_column(Float, default=0.0)
    out_errors: Mapped[int] = mapped_column(Integer, default=0)
    out_discards: Mapped[int] = mapped_column(Integer, default=0)
    
    # Error counters
    crc_errors: Mapped[int] = mapped_column(Integer, default=0)
    frame_errors: Mapped[int] = mapped_column(Integer, default=0)
    collision_count: Mapped[int] = mapped_column(Integer, default=0)
    
    # Connection information
    connected_to: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    description: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_seen: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    last_check: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    # Relationships
    device: Mapped["Device"] = relationship("Device", back_populates="ports")
    
    # Link relationships
    source_links: Mapped[List["Link"]] = relationship(
        "Link",
        foreign_keys="Link.source_port_id",
        back_populates="source_port",
        cascade="all, delete-orphan"
    )
    target_links: Mapped[List["Link"]] = relationship(
        "Link",
        foreign_keys="Link.target_port_id",
        back_populates="target_port",
        cascade="all, delete-orphan"
    )
    
    # FIXED: Added missing 'events' relationship
    events: Mapped[List["Event"]] = relationship(
        "Event",
        back_populates="port",
        cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<Port {self.port_name} on Device {self.device_id}>"