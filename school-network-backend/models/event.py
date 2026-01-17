"""
Event model for tracking network events and alerts.
"""

from sqlalchemy import Column, Integer, String, DateTime, Boolean, Enum, ForeignKey, JSON, Index
from sqlalchemy.orm import relationship
from database import Base
from datetime import datetime
from enum import Enum as PyEnum


class EventTypeEnum(str, PyEnum):
    """Types of network events."""
    # Device Events
    DEVICE_UP = "DEVICE_UP"
    DEVICE_DOWN = "DEVICE_DOWN"
    DEVICE_DISCOVERED = "DEVICE_DISCOVERED"
    DEVICE_REMOVED = "DEVICE_REMOVED"
    DEVICE_UNREACHABLE = "DEVICE_UNREACHABLE"
    
    # Port Events
    PORT_UP = "PORT_UP"
    PORT_DOWN = "PORT_DOWN"
    PORT_ERROR = "PORT_ERROR"
    PORT_DISABLED = "PORT_DISABLED"
    
    # Link Events
    LINK_UP = "LINK_UP"
    LINK_DOWN = "LINK_DOWN"
    LINK_DEGRADED = "LINK_DEGRADED"
    
    # Performance Events
    HIGH_LATENCY = "HIGH_LATENCY"
    HIGH_PACKET_LOSS = "HIGH_PACKET_LOSS"
    HIGH_JITTER = "HIGH_JITTER"
    BANDWIDTH_THRESHOLD = "BANDWIDTH_THRESHOLD"
    
    # Cable Health Events
    CABLE_HEALTH_DEGRADED = "CABLE_HEALTH_DEGRADED"
    CABLE_HEALTH_CRITICAL = "CABLE_HEALTH_CRITICAL"
    CABLE_HEALTH_EXCELLENT = "CABLE_HEALTH_EXCELLENT"
    
    # Configuration Events
    CONFIGURATION_CHANGE = "CONFIGURATION_CHANGE"
    FIRMWARE_UPDATE = "FIRMWARE_UPDATE"
    
    # Security Events
    SECURITY_ALERT = "SECURITY_ALERT"
    UNAUTHORIZED_ACCESS = "UNAUTHORIZED_ACCESS"
    UNUSUAL_TRAFFIC = "UNUSUAL_TRAFFIC"
    
    # Backup Events
    BACKUP_COMPLETED = "BACKUP_COMPLETED"
    BACKUP_FAILED = "BACKUP_FAILED"
    
    # Discovery Events
    SCAN_COMPLETED = "SCAN_COMPLETED"
    SCAN_FAILED = "SCAN_FAILED"
    SCAN_STARTED = "SCAN_STARTED"
    
    # System Events
    SYSTEM_STARTUP = "SYSTEM_STARTUP"
    SYSTEM_SHUTDOWN = "SYSTEM_SHUTDOWN"
    MONITORING_STARTED = "MONITORING_STARTED"
    MONITORING_STOPPED = "MONITORING_STOPPED"
    
    # General
    UNKNOWN = "UNKNOWN"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"


class EventSeverityEnum(str, PyEnum):
    """Severity levels for events."""
    CRITICAL = "CRITICAL"  # Immediate action required
    HIGH = "HIGH"          # Action required soon
    MEDIUM = "MEDIUM"      # Should be addressed
    LOW = "LOW"            # Minor issue
    INFO = "INFO"          # Informational only


class Event(Base):
    """
    Event model for tracking all network events and alerts.
    
    Stores events related to devices, ports, links, and system operations.
    Supports event acknowledgement and detailed logging.
    """
    __tablename__ = "events"

    # Primary key
    id = Column(String, primary_key=True, index=True)
    
    # Event classification
    event_type = Column(Enum(EventTypeEnum), nullable=False, index=True)
    severity = Column(Enum(EventSeverityEnum), nullable=False, index=True)
    
    # Related entities (nullable - not all events relate to specific entities)
    device_id = Column(
        String,
        ForeignKey("devices.id", ondelete="CASCADE"),
        nullable=True,
        index=True
    )
    port_id = Column(
        String,
        ForeignKey("ports.id", ondelete="CASCADE"),
        nullable=True,
        index=True
    )
    link_id = Column(
        String,
        ForeignKey("links.id", ondelete="CASCADE"),
        nullable=True,
        index=True
    )
    
    # Event details
    message = Column(String(1000), nullable=False)
    details = Column(JSON, nullable=True)  # Additional structured data
    source = Column(String(100), nullable=True, index=True)  # Source system/module
    
    # Acknowledgement
    acknowledged = Column(Boolean, default=False, index=True)
    acknowledged_by = Column(String(100), nullable=True)
    acknowledged_at = Column(DateTime, nullable=True)
    notes = Column(String(1000), nullable=True)  # Admin notes
    
    # Resolution
    resolved = Column(Boolean, default=False, index=True)
    resolved_by = Column(String(100), nullable=True)
    resolved_at = Column(DateTime, nullable=True)
    resolution_notes = Column(String(1000), nullable=True)
    
    # Auto-resolve (for transient events)
    auto_resolved = Column(Boolean, default=False)
    
    # Notification
    notification_sent = Column(Boolean, default=False)
    notification_sent_at = Column(DateTime, nullable=True)
    
    # Recurrence tracking
    occurrence_count = Column(Integer, default=1)
    first_occurred_at = Column(DateTime, default=datetime.utcnow)
    last_occurred_at = Column(DateTime, default=datetime.utcnow)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, index=True, nullable=False)
    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False
    )
    
    # Relationships
    device = relationship("Device", back_populates="events")
    port = relationship("Port", back_populates="events")
    link = relationship("Link", back_populates="events")
    
    # Indexes for common queries
    __table_args__ = (
        Index('idx_event_type_severity', 'event_type', 'severity'),
        Index('idx_event_created_at', 'created_at'),
        Index('idx_event_acknowledged', 'acknowledged', 'created_at'),
        Index('idx_event_device_type', 'device_id', 'event_type'),
        Index('idx_event_severity_created', 'severity', 'created_at'),
    )

    def __repr__(self):
        return f"<Event {self.id}: {self.event_type.value} - {self.severity.value}>"

    def acknowledge(self, acknowledged_by: str, notes: str = None): # type: ignore
        """
        Acknowledge this event.
        
        Args:
            acknowledged_by: Username or identifier of person acknowledging
            notes: Optional notes about the acknowledgement
        """
        self.acknowledged = True
        self.acknowledged_by = acknowledged_by
        self.acknowledged_at = datetime.utcnow()
        if notes:
            self.notes = notes
        self.updated_at = datetime.utcnow()

    def resolve(self, resolved_by: str, resolution_notes: str = None): # type: ignore
        """
        Mark this event as resolved.
        
        Args:
            resolved_by: Username or identifier of person resolving
            resolution_notes: Optional notes about the resolution
        """
        self.resolved = True
        self.resolved_by = resolved_by
        self.resolved_at = datetime.utcnow()
        if resolution_notes:
            self.resolution_notes = resolution_notes
        
        # Auto-acknowledge if not already acknowledged
        if not self.acknowledged: # type: ignore
            self.acknowledge(resolved_by, "Auto-acknowledged on resolution")
        
        self.updated_at = datetime.utcnow()

    def increment_occurrence(self):
        """Increment occurrence count for recurring events."""
        self.occurrence_count += 1
        self.last_occurred_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()

    def is_critical(self) -> bool:
        """Check if event is critical severity."""
        return self.severity == EventSeverityEnum.CRITICAL # type: ignore

    def is_high_priority(self) -> bool:
        """Check if event is high priority (CRITICAL or HIGH)."""
        return self.severity in [EventSeverityEnum.CRITICAL, EventSeverityEnum.HIGH]

    def is_device_event(self) -> bool:
        """Check if this is a device-related event."""
        return self.device_id is not None

    def is_link_event(self) -> bool:
        """Check if this is a link-related event."""
        return self.link_id is not None

    def is_port_event(self) -> bool:
        """Check if this is a port-related event."""
        return self.port_id is not None

    def requires_attention(self) -> bool:
        """Check if event requires attention (not acknowledged and high priority)."""
        return not self.acknowledged and self.is_high_priority() # type: ignore

    @property
    def age_seconds(self) -> float:
        """Get age of event in seconds."""
        return (datetime.utcnow() - self.created_at).total_seconds()

    @property
    def age_minutes(self) -> float:
        """Get age of event in minutes."""
        return self.age_seconds / 60

    @property
    def age_hours(self) -> float:
        """Get age of event in hours."""
        return self.age_minutes / 60

    def to_dict(self) -> dict:
        """Convert event to dictionary representation."""
        return {
            "id": self.id,
            "event_type": self.event_type.value,
            "severity": self.severity.value,
            "device_id": self.device_id,
            "port_id": self.port_id,
            "link_id": self.link_id,
            "message": self.message,
            "details": self.details,
            "source": self.source,
            "acknowledged": self.acknowledged,
            "acknowledged_by": self.acknowledged_by,
            "acknowledged_at": self.acknowledged_at.isoformat() if self.acknowledged_at else None, # type: ignore
            "notes": self.notes,
            "resolved": self.resolved,
            "resolved_by": self.resolved_by,
            "resolved_at": self.resolved_at.isoformat() if self.resolved_at else None, # type: ignore
            "resolution_notes": self.resolution_notes,
            "occurrence_count": self.occurrence_count,
            "first_occurred_at": self.first_occurred_at.isoformat() if self.first_occurred_at else None, # type: ignore
            "last_occurred_at": self.last_occurred_at.isoformat() if self.last_occurred_at else None, # type: ignore
            "created_at": self.created_at.isoformat() if self.created_at else None, # type: ignore
            "updated_at": self.updated_at.isoformat() if self.updated_at else None, # type: ignore
            "age_minutes": self.age_minutes,
        }