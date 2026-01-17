from sqlalchemy import Column, String, Integer, DateTime, Float, Boolean, ForeignKey, Enum
from sqlalchemy.orm import relationship
from database import Base
from datetime import datetime
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


class Device(Base):
    __tablename__ = "devices"

    id = Column(String, primary_key=True)
    name = Column(String(255), nullable=False, index=True)
    device_type = Column(Enum(DeviceTypeEnum), nullable=False, index=True)
    ip = Column(String(45), unique=True, nullable=True, index=True)
    mac = Column(String(17), unique=True, nullable=True, index=True)
    hostname = Column(String(255), nullable=True)
    location = Column(String(255), nullable=True)
    description = Column(String(500), nullable=True)
    
    # Status tracking
    status = Column(Enum(DeviceStatusEnum), default=DeviceStatusEnum.UNKNOWN, index=True)
    last_seen = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_monitored = Column(Boolean, default=True)
    
    # Network info
    vlan_id = Column(Integer, nullable=True)
    subnet = Column(String(45), nullable=True)
    
    # SNMP
    snmp_enabled = Column(Boolean, default=False)
    snmp_community = Column(String(255), nullable=True)
    snmp_version = Column(String(5), default="2c")
    
    # Position on topology map
    position_x = Column(Float, nullable=True)
    position_y = Column(Float, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    ports = relationship("Port", back_populates="device", cascade="all, delete-orphan")
    from_links = relationship(
        "Link",
        foreign_keys="Link.source_device_id",
        back_populates="source_device",
        cascade="all, delete-orphan"
    )
    to_links = relationship(
        "Link",
        foreign_keys="Link.target_device_id",
        back_populates="target_device",
        cascade="all, delete-orphan"
    )
    events = relationship("Event", back_populates="device", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Device {self.name} ({self.device_type})>"