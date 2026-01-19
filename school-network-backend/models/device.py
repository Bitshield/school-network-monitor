from sqlalchemy import String, Integer, DateTime, Float, Boolean, Enum as SQLEnum
from sqlalchemy.orm import relationship, Mapped, mapped_column
from database import Base
from datetime import datetime
from enum import Enum as PyEnum
from typing import Optional, List, TYPE_CHECKING

if TYPE_CHECKING:
    from models.port import Port
    from models.link import Link
    from models.event import Event


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


class Device(Base):
    __tablename__ = "devices"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    device_type: Mapped[DeviceTypeEnum] = mapped_column(SQLEnum(DeviceTypeEnum), nullable=False, index=True)
    ip: Mapped[Optional[str]] = mapped_column(String(45), unique=True, nullable=True, index=True)
    mac: Mapped[Optional[str]] = mapped_column(String(17), unique=True, nullable=True, index=True)
    hostname: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    location: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    description: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    
    # Status tracking
    status: Mapped[DeviceStatusEnum] = mapped_column(SQLEnum(DeviceStatusEnum), default=DeviceStatusEnum.UNKNOWN, index=True)
    last_seen: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_monitored: Mapped[bool] = mapped_column(Boolean, default=True)
    
    # Network info
    vlan_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    subnet: Mapped[Optional[str]] = mapped_column(String(45), nullable=True)
    
    # SNMP
    snmp_enabled: Mapped[bool] = mapped_column(Boolean, default=False)
    snmp_community: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    snmp_version: Mapped[str] = mapped_column(String(5), default="2c")
    
    # Position on topology map
    position_x: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    position_y: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    ports: Mapped[List["Port"]] = relationship("Port", back_populates="device", cascade="all, delete-orphan")
    from_links: Mapped[List["Link"]] = relationship(
        "Link",
        foreign_keys="Link.source_device_id",
        back_populates="source_device",
        cascade="all, delete-orphan"
    )
    to_links: Mapped[List["Link"]] = relationship(
        "Link",
        foreign_keys="Link.target_device_id",
        back_populates="target_device",
        cascade="all, delete-orphan"
    )
    events: Mapped[List["Event"]] = relationship("Event", back_populates="device", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Device {self.name} ({self.device_type})>"