from sqlalchemy import String, Integer, DateTime, Enum as SQLEnum, ForeignKey
from sqlalchemy.orm import relationship, Mapped, mapped_column
from database import Base
from datetime import datetime
from enum import Enum as PyEnum
from typing import Optional, List, TYPE_CHECKING

if TYPE_CHECKING:
    from models.device import Device
    from models.link import Link


class PortStatusEnum(str, PyEnum):
    UP = "UP"
    DOWN = "DOWN"
    UNKNOWN = "UNKNOWN"


class PortTypeEnum(str, PyEnum):
    ETHERNET = "ETHERNET"
    FIBER = "FIBER"
    WIRELESS = "WIRELESS"
    VIRTUAL = "VIRTUAL"
    UNKNOWN = "UNKNOWN"


class Port(Base):
    __tablename__ = "ports"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    device_id: Mapped[str] = mapped_column(String, ForeignKey("devices.id", ondelete="CASCADE"), nullable=False, index=True)
    port_name: Mapped[str] = mapped_column(String(100), nullable=False)
    port_number: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    port_type: Mapped[PortTypeEnum] = mapped_column(SQLEnum(PortTypeEnum), default=PortTypeEnum.UNKNOWN)
    
    # Port status
    status: Mapped[PortStatusEnum] = mapped_column(SQLEnum(PortStatusEnum), default=PortStatusEnum.UNKNOWN)
    admin_status: Mapped[str] = mapped_column(String(20), default="UP")
    
    # Port properties
    speed_mbps: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    duplex: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    mac_address: Mapped[Optional[str]] = mapped_column(String(17), nullable=True)
    
    # VLAN
    vlan_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    
    # Description
    description: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    checked_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    # Relationships
    device: Mapped["Device"] = relationship("Device", back_populates="ports")
    outgoing_links: Mapped[List["Link"]] = relationship(
        "Link",
        foreign_keys="Link.source_port_id",
        back_populates="source_port"
    )
    incoming_links: Mapped[List["Link"]] = relationship(
        "Link",
        foreign_keys="Link.target_port_id",
        back_populates="target_port"
    )

    def __repr__(self):
        return f"<Port {self.port_name} on Device {self.device_id}>"