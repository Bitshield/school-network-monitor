"""
Application-wide constants and enumerations.
"""

from enum import Enum


class DeviceType(str, Enum):
    """Network device types."""
    ROUTER = "ROUTER"
    SWITCH = "SWITCH"
    SERVER = "SERVER"
    PC = "PC"
    AP = "AP"  # Access Point
    PRINTER = "PRINTER"
    CAMERA = "CAMERA"
    FIREWALL = "FIREWALL"
    LOAD_BALANCER = "LOAD_BALANCER"
    UNKNOWN = "UNKNOWN"


class DeviceStatus(str, Enum):
    """Device operational status."""
    UP = "UP"
    DOWN = "DOWN"
    UNREACHABLE = "UNREACHABLE"
    UNKNOWN = "UNKNOWN"
    MAINTENANCE = "MAINTENANCE"


class PortStatus(str, Enum):
    """Port operational status."""
    UP = "UP"
    DOWN = "DOWN"
    DISABLED = "DISABLED"
    ERROR = "ERROR"
    UNKNOWN = "UNKNOWN"
    TESTING = "TESTING"


class PortType(str, Enum):
    """Port interface types."""
    ETHERNET = "ETHERNET"
    FIBER = "FIBER"
    SFP = "SFP"
    SFP_PLUS = "SFP+"
    QSFP = "QSFP"
    QSFP28 = "QSFP28"
    VIRTUAL = "VIRTUAL"
    LOOPBACK = "LOOPBACK"
    UNKNOWN = "UNKNOWN"


class LinkStatus(str, Enum):
    """Link operational status."""
    UP = "UP"
    DOWN = "DOWN"
    DEGRADED = "DEGRADED"
    UNKNOWN = "UNKNOWN"


class LinkType(str, Enum):
    """Link connection types."""
    PHYSICAL = "PHYSICAL"
    LOGICAL = "LOGICAL"
    VIRTUAL = "VIRTUAL"
    TUNNEL = "TUNNEL"
    UNKNOWN = "UNKNOWN"


class CableType(str, Enum):
    """Cable types."""
    CAT5 = "CAT5"
    CAT5E = "CAT5E"
    CAT6 = "CAT6"
    CAT6A = "CAT6A"
    CAT7 = "CAT7"
    CAT8 = "CAT8"
    FIBER_SM = "FIBER_SM"  # Single-mode fiber
    FIBER_MM = "FIBER_MM"  # Multi-mode fiber
    COAX = "COAX"
    UNKNOWN = "UNKNOWN"


class CableHealthStatus(str, Enum):
    """Cable health status."""
    EXCELLENT = "EXCELLENT"
    GOOD = "GOOD"
    FAIR = "FAIR"
    POOR = "POOR"
    CRITICAL = "CRITICAL"
    UNKNOWN = "UNKNOWN"


class EventType(str, Enum):
    """Event types."""
    # Device Events
    DEVICE_UP = "DEVICE_UP"
    DEVICE_DOWN = "DEVICE_DOWN"
    DEVICE_DISCOVERED = "DEVICE_DISCOVERED"
    DEVICE_REMOVED = "DEVICE_REMOVED"
    
    # Port Events
    PORT_UP = "PORT_UP"
    PORT_DOWN = "PORT_DOWN"
    
    # Link Events
    LINK_UP = "LINK_UP"
    LINK_DOWN = "LINK_DOWN"
    LINK_DEGRADED = "LINK_DEGRADED"
    
    # Performance Events
    HIGH_LATENCY = "HIGH_LATENCY"
    HIGH_PACKET_LOSS = "HIGH_PACKET_LOSS"
    HIGH_JITTER = "HIGH_JITTER"
    
    # Cable Health Events
    CABLE_HEALTH_DEGRADED = "CABLE_HEALTH_DEGRADED"
    CABLE_HEALTH_CRITICAL = "CABLE_HEALTH_CRITICAL"
    
    # Configuration Events
    CONFIGURATION_CHANGE = "CONFIGURATION_CHANGE"
    
    # Security Events
    SECURITY_ALERT = "SECURITY_ALERT"
    
    # System Events
    SCAN_COMPLETED = "SCAN_COMPLETED"
    SCAN_FAILED = "SCAN_FAILED"
    BACKUP_COMPLETED = "BACKUP_COMPLETED"
    BACKUP_FAILED = "BACKUP_FAILED"
    
    UNKNOWN = "UNKNOWN"


class EventSeverity(str, Enum):
    """Event severity levels."""
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"
    INFO = "INFO"


class ProtocolType(str, Enum):
    """Network protocol types."""
    TCP = "TCP"
    UDP = "UDP"
    ICMP = "ICMP"
    HTTP = "HTTP"
    HTTPS = "HTTPS"
    SSH = "SSH"
    TELNET = "TELNET"
    SNMP = "SNMP"
    FTP = "FTP"
    DNS = "DNS"
    DHCP = "DHCP"
    UNKNOWN = "UNKNOWN"


class SNMPVersion(str, Enum):
    """SNMP protocol versions."""
    V1 = "1"
    V2C = "2c"
    V3 = "3"


# Network Constants
PRIVATE_IP_RANGES = [
    "10.0.0.0/8",
    "172.16.0.0/12",
    "192.168.0.0/16",
]

RESERVED_IP_RANGES = [
    "127.0.0.0/8",    # Loopback
    "169.254.0.0/16", # Link-local
    "224.0.0.0/4",    # Multicast
    "240.0.0.0/4",    # Reserved
]

# Port Constants
WELL_KNOWN_PORTS = {
    20: "FTP Data",
    21: "FTP Control",
    22: "SSH",
    23: "Telnet",
    25: "SMTP",
    53: "DNS",
    67: "DHCP Server",
    68: "DHCP Client",
    80: "HTTP",
    110: "POP3",
    143: "IMAP",
    161: "SNMP",
    162: "SNMP Trap",
    443: "HTTPS",
    3306: "MySQL",
    5432: "PostgreSQL",
    8080: "HTTP Alt",
}

# Standard Network Speeds (in Mbps)
NETWORK_SPEEDS = {
    "10BASE-T": 10,
    "100BASE-TX": 100,
    "1000BASE-T": 1000,
    "10GBASE-T": 10000,
    "25GBASE": 25000,
    "40GBASE": 40000,
    "100GBASE": 100000,
    "200GBASE": 200000,
    "400GBASE": 400000,
}

# Cable Maximum Lengths (in meters)
CABLE_MAX_LENGTHS = {
    CableType.CAT5: 100,
    CableType.CAT5E: 100,
    CableType.CAT6: 100,
    CableType.CAT6A: 100,
    CableType.CAT7: 100,
    CableType.CAT8: 30,
    CableType.FIBER_SM: 40000,  # 40km
    CableType.FIBER_MM: 2000,   # 2km
    CableType.COAX: 500,
}

# Cable Speed Capabilities (in Mbps)
CABLE_SPEED_CAPABILITIES = {
    CableType.CAT5: 100,
    CableType.CAT5E: 1000,
    CableType.CAT6: 10000,
    CableType.CAT6A: 10000,
    CableType.CAT7: 10000,
    CableType.CAT8: 40000,
    CableType.FIBER_SM: 100000,
    CableType.FIBER_MM: 40000,
    CableType.COAX: 1000,
}

# Health Score Thresholds
HEALTH_SCORE_THRESHOLDS = {
    "EXCELLENT": 90,
    "GOOD": 80,
    "FAIR": 60,
    "POOR": 40,
    "CRITICAL": 0,
}

# Performance Thresholds
LATENCY_THRESHOLDS = {
    "GOOD": 10,      # < 10ms
    "WARNING": 50,   # 10-50ms
    "CRITICAL": 100, # > 100ms
}

PACKET_LOSS_THRESHOLDS = {
    "GOOD": 0.1,     # < 0.1%
    "WARNING": 1.0,  # 0.1-1%
    "CRITICAL": 5.0, # > 5%
}

JITTER_THRESHOLDS = {
    "GOOD": 5,       # < 5ms
    "WARNING": 10,   # 5-10ms
    "CRITICAL": 20,  # > 20ms
}

# MAC Address OUI Vendors (Organizationally Unique Identifier)
MAC_OUI_VENDORS = {
    "00:0A:95": "Cisco",
    "00:1A:2F": "Cisco",
    "00:1B:D4": "Cisco",
    "00:1C:0E": "Cisco",
    "00:24:C4": "HP",
    "00:22:55": "3Com",
    "00:50:56": "VMware",
    "08:00:27": "VirtualBox",
    "00:1C:42": "Parallels",
    "BC:52:B7": "Netgear",
    "54:E6:FC": "ASUS",
    "00:21:6A": "Tenda",
    "D8:50:E6": "TP-Link",
    "F0:9F:C2": "Ubiquiti",
}

# API Response Messages
API_MESSAGES = {
    "SUCCESS": "Operation completed successfully",
    "CREATED": "Resource created successfully",
    "UPDATED": "Resource updated successfully",
    "DELETED": "Resource deleted successfully",
    "NOT_FOUND": "Resource not found",
    "VALIDATION_ERROR": "Validation error",
    "SERVER_ERROR": "Internal server error",
    "UNAUTHORIZED": "Unauthorized access",
    "FORBIDDEN": "Access forbidden",
}

# Monitoring Intervals (in seconds)
DEFAULT_MONITORING_INTERVALS = {
    "DEVICE_CHECK": 60,
    "PORT_CHECK": 120,
    "LINK_CHECK": 60,
    "CABLE_HEALTH": 300,
    "DISCOVERY_SCAN": 3600,
}

# Pagination Defaults
DEFAULT_PAGE_SIZE = 50
MAX_PAGE_SIZE = 1000

# Rate Limiting
RATE_LIMIT_PER_MINUTE = 60
RATE_LIMIT_PER_HOUR = 1000

# File Upload Limits
MAX_FILE_SIZE_MB = 10
ALLOWED_FILE_EXTENSIONS = [".csv", ".json", ".xlsx", ".txt"]

# WebSocket Constants
WS_HEARTBEAT_INTERVAL = 30
WS_MESSAGE_TYPES = {
    "DEVICE_STATUS": "device_status",
    "LINK_STATUS": "link_status",
    "EVENT": "event",
    "ALERT": "alert",
    "TOPOLOGY_UPDATE": "topology_update",
}

# Database Constants
DB_POOL_SIZE = 10
DB_MAX_OVERFLOW = 20
DB_POOL_RECYCLE = 3600  # 1 hour

# Cache TTL (in seconds)
CACHE_TTL = {
    "SHORT": 60,      # 1 minute
    "MEDIUM": 300,    # 5 minutes
    "LONG": 3600,     # 1 hour
    "VERY_LONG": 86400, # 24 hours
}

# Regex Patterns
REGEX_PATTERNS = {
    "IP_ADDRESS": r"^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$",
    "MAC_ADDRESS": r"^([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})$",
    "HOSTNAME": r"^[a-zA-Z0-9]([a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?(\.[a-zA-Z0-9]([a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?)*$",
    "CIDR": r"^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\/(?:[0-9]|[1-2][0-9]|3[0-2])$",
}

# HTTP Status Code Messages
HTTP_STATUS_MESSAGES = {
    200: "OK",
    201: "Created",
    204: "No Content",
    400: "Bad Request",
    401: "Unauthorized",
    403: "Forbidden",
    404: "Not Found",
    422: "Unprocessable Entity",
    500: "Internal Server Error",
    503: "Service Unavailable",
}