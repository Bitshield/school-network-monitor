from sqlalchemy import Column, String, Integer, DateTime, Float, Boolean, ForeignKey, Enum
from sqlalchemy.orm import relationship
from database import Base
from datetime import datetime
from enum import Enum as PyEnum


class PortStatusEnum(str, PyEnum):
    UP = "UP"
    DOWN = "DOWN"
    DISABLED = "DISABLED"
    ERROR = "ERROR"
    UNKNOWN = "UNKNOWN"


class PortTypeEnum(str, PyEnum):
    ETHERNET = "ETHERNET"
    FIBER = "FIBER"
    SFP = "SFP"
    SFP_PLUS = "SFP+"
    QSFP = "QSFP"
    VIRTUAL = "VIRTUAL"
    UNKNOWN = "UNKNOWN"


class Port(Base):
    __tablename__ = "ports"

    id = Column(String, primary_key=True)
    device_id = Column(String, ForeignKey("devices.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Port identification
    name = Column(String(100), nullable=False)  # User-friendly name
    port_number = Column(Integer, nullable=False)  # Physical port number
    port_name = Column(String(50), nullable=False)  # System name: Gi0/0/1, eth0, etc.
    
    # Port type and status
    port_type = Column(Enum(PortTypeEnum), default=PortTypeEnum.ETHERNET)
    status = Column(Enum(PortStatusEnum), default=PortStatusEnum.UNKNOWN, index=True)
    is_up = Column(Boolean, default=False)
    
    # Port specifications
    speed_mbps = Column(Float, nullable=True)  # Current speed
    max_speed_mbps = Column(Float, nullable=True)  # Maximum supported speed
    mtu = Column(Integer, nullable=True)
    duplex = Column(String(50), nullable=True)  # Full, Half
    
    # VLAN information
    vlan_id = Column(Integer, nullable=True)
    is_trunk = Column(Boolean, default=False)
    allowed_vlans = Column(String(255), nullable=True)  # e.g., "1,10,20-30"
    native_vlan = Column(Integer, nullable=True)
    
    # MAC address
    mac_address = Column(String(17), nullable=True)
    
    # Statistics - Received
    rx_bytes = Column(Integer, default=0)
    rx_packets = Column(Integer, default=0)
    rx_errors = Column(Integer, default=0)
    rx_dropped = Column(Integer, default=0)
    in_octets = Column(Float, default=0.0)
    in_discards = Column(Integer, default=0)
    
    # Statistics - Transmitted
    tx_bytes = Column(Integer, default=0)
    tx_packets = Column(Integer, default=0)
    tx_errors = Column(Integer, default=0)
    tx_dropped = Column(Integer, default=0)
    out_octets = Column(Float, default=0.0)
    out_errors = Column(Integer, default=0)
    out_discards = Column(Integer, default=0)
    
    # Error counters
    crc_errors = Column(Integer, default=0)
    frame_errors = Column(Integer, default=0)
    collision_count = Column(Integer, default=0)
    
    # Connected device info
    connected_to = Column(String(255), nullable=True)
    description = Column(String(500), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_seen = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_check = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    device = relationship("Device", back_populates="ports")
    source_links = relationship(
        "Link",
        foreign_keys="Link.source_port_id",
        back_populates="source_port"
    )
    target_links = relationship(
        "Link",
        foreign_keys="Link.target_port_id",
        back_populates="target_port"
    )
    events = relationship(
        "Event",
        back_populates="port",
        cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<Port {self.device_id}:{self.port_name}>"