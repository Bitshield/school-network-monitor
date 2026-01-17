"""
Data validation service for network configurations.
"""

from typing import Dict, List, Optional, Tuple
import ipaddress
import re
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class NetworkValidator:
    """Validate network-related data."""

    @staticmethod
    def validate_ip(ip: str) -> Tuple[bool, Optional[str]]:
        """
        Validate IP address format.
        
        Args:
            ip: IP address string
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        try:
            ipaddress.ip_address(ip)
            return True, None
        except ValueError as e:
            return False, f"Invalid IP address: {str(e)}"

    @staticmethod
    def validate_ip_range(ip_range: str) -> Tuple[bool, Optional[str]]:
        """
        Validate IP range in CIDR notation.
        
        Args:
            ip_range: IP range string (e.g., "192.168.1.0/24")
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        try:
            ipaddress.ip_network(ip_range, strict=False)
            return True, None
        except ValueError as e:
            return False, f"Invalid IP range: {str(e)}"

    @staticmethod
    def validate_mac(mac: str) -> Tuple[bool, Optional[str]]:
        """
        Validate MAC address format.
        
        Args:
            mac: MAC address string
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        # Accept both : and - as separators
        pattern = r'^([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})$'
        if re.match(pattern, mac):
            return True, None
        return False, "Invalid MAC address format. Expected: XX:XX:XX:XX:XX:XX or XX-XX-XX-XX-XX-XX"

    @staticmethod
    def normalize_mac(mac: str) -> str:
        """
        Normalize MAC address to standard format (uppercase with colons).
        
        Args:
            mac: MAC address string
            
        Returns:
            Normalized MAC address
        """
        # Remove all separators and convert to uppercase
        clean_mac = mac.replace(':', '').replace('-', '').upper()
        # Add colons every 2 characters
        return ':'.join(clean_mac[i:i+2] for i in range(0, 12, 2))

    @staticmethod
    def validate_port_number(port: int) -> Tuple[bool, Optional[str]]:
        """
        Validate network port number.
        
        Args:
            port: Port number
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if 1 <= port <= 65535:
            return True, None
        return False, "Port number must be between 1 and 65535"

    @staticmethod
    def validate_vlan_id(vlan_id: int) -> Tuple[bool, Optional[str]]:
        """
        Validate VLAN ID.
        
        Args:
            vlan_id: VLAN ID
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if 1 <= vlan_id <= 4094:
            return True, None
        return False, "VLAN ID must be between 1 and 4094"

    @staticmethod
    def validate_subnet_mask(mask: str) -> Tuple[bool, Optional[str]]:
        """
        Validate subnet mask.
        
        Args:
            mask: Subnet mask (e.g., "255.255.255.0" or "/24")
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        # Check if it's CIDR notation
        if mask.startswith('/'):
            try:
                prefix_len = int(mask[1:])
                if 0 <= prefix_len <= 32:
                    return True, None
                return False, "CIDR prefix length must be between 0 and 32"
            except ValueError:
                return False, "Invalid CIDR notation"
        
        # Check if it's dotted decimal notation
        try:
            ip = ipaddress.IPv4Address(mask)
            # Check if it's a valid subnet mask (all 1s followed by all 0s)
            mask_int = int(ip)
            # Valid mask should have no 0 bits before 1 bits
            inverted = ~mask_int & 0xFFFFFFFF
            if (inverted & (inverted + 1)) == 0:
                return True, None
            return False, "Invalid subnet mask (must be contiguous 1s followed by 0s)"
        except ValueError:
            return False, "Invalid subnet mask format"

    @staticmethod
    def ip_in_subnet(ip: str, subnet: str) -> bool:
        """
        Check if IP address is in subnet.
        
        Args:
            ip: IP address
            subnet: Subnet in CIDR notation
            
        Returns:
            True if IP is in subnet, False otherwise
        """
        try:
            ip_obj = ipaddress.ip_address(ip)
            network = ipaddress.ip_network(subnet, strict=False)
            return ip_obj in network
        except ValueError:
            return False

    @staticmethod
    def validate_hostname(hostname: str) -> Tuple[bool, Optional[str]]:
        """
        Validate hostname format.
        
        Args:
            hostname: Hostname string
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        # RFC 1123 hostname validation
        if len(hostname) > 255:
            return False, "Hostname too long (max 255 characters)"
        
        if hostname[-1] == ".":
            hostname = hostname[:-1]  # Strip trailing dot
        
        pattern = r'^[a-zA-Z0-9]([a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?(\.[a-zA-Z0-9]([a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?)*$'
        if re.match(pattern, hostname):
            return True, None
        return False, "Invalid hostname format"


class DeviceValidator:
    """Validate device-related data."""

    @staticmethod
    def validate_device_name(name: str) -> Tuple[bool, Optional[str]]:
        """
        Validate device name.
        
        Args:
            name: Device name
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not name or len(name.strip()) == 0:
            return False, "Device name cannot be empty"
        
        if len(name) > 255:
            return False, "Device name too long (max 255 characters)"
        
        # Check for invalid characters
        invalid_chars = ['<', '>', '&', '"', "'", '\\', '/', '\n', '\r', '\t']
        for char in invalid_chars:
            if char in name:
                return False, f"Device name contains invalid character: {char}"
        
        return True, None

    @staticmethod
    def validate_snmp_community(community: str) -> Tuple[bool, Optional[str]]:
        """
        Validate SNMP community string.
        
        Args:
            community: SNMP community string
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not community:
            return False, "SNMP community string cannot be empty"
        
        if len(community) > 255:
            return False, "SNMP community string too long (max 255 characters)"
        
        # Community strings should be ASCII printable characters
        if not all(32 <= ord(c) <= 126 for c in community):
            return False, "SNMP community string contains invalid characters"
        
        return True, None


class LinkValidator:
    """Validate link-related data."""

    @staticmethod
    def validate_bandwidth(bandwidth: int) -> Tuple[bool, Optional[str]]:
        """
        Validate bandwidth value.
        
        Args:
            bandwidth: Bandwidth in Mbps
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if bandwidth < 0:
            return False, "Bandwidth cannot be negative"
        
        if bandwidth > 400000:  # 400 Gbps max
            return False, "Bandwidth exceeds maximum (400 Gbps)"
        
        # Check if it's a common standard value
        common_speeds = [10, 100, 1000, 10000, 25000, 40000, 100000, 200000, 400000]
        if bandwidth not in common_speeds:
            logger.warning(f"Bandwidth {bandwidth} Mbps is not a standard speed")
        
        return True, None

    @staticmethod
    def validate_latency(latency: float) -> Tuple[bool, Optional[str]]:
        """
        Validate latency value.
        
        Args:
            latency: Latency in milliseconds
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if latency < 0:
            return False, "Latency cannot be negative"
        
        if latency > 10000:  # 10 seconds max
            return False, "Latency exceeds reasonable maximum (10 seconds)"
        
        if latency > 1000:  # 1 second
            logger.warning(f"Latency {latency}ms is unusually high")
        
        return True, None

    @staticmethod
    def validate_link_endpoints(source_id: str, target_id: str) -> Tuple[bool, Optional[str]]:
        """
        Validate link endpoints.
        
        Args:
            source_id: Source device/port ID
            target_id: Target device/port ID
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not source_id or not target_id:
            return False, "Link endpoints cannot be empty"
        
        if source_id == target_id:
            return False, "Source and target cannot be the same"
        
        return True, None


class ConfigValidator:
    """Validate configuration data."""

    @staticmethod
    def validate_monitoring_interval(interval: int) -> Tuple[bool, Optional[str]]:
        """
        Validate monitoring interval.
        
        Args:
            interval: Interval in seconds
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if interval < 10:
            return False, "Monitoring interval too short (minimum 10 seconds)"
        
        if interval > 86400:  # 24 hours
            return False, "Monitoring interval too long (maximum 24 hours)"
        
        return True, None

    @staticmethod
    def validate_threshold(
        value: float,
        min_val: float,
        max_val: float,
        name: str
    ) -> Tuple[bool, Optional[str]]:
        """
        Validate threshold value.
        
        Args:
            value: Threshold value
            min_val: Minimum allowed value
            max_val: Maximum allowed value
            name: Threshold name (for error messages)
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if value < min_val:
            return False, f"{name} below minimum ({min_val})"
        
        if value > max_val:
            return False, f"{name} exceeds maximum ({max_val})"
        
        return True, None


class ValidationService:
    """
    Unified validation service combining all validators.
    """

    def __init__(self):
        self.network = NetworkValidator()
        self.device = DeviceValidator()
        self.link = LinkValidator()
        self.config = ConfigValidator()

    def validate_device_data(self, data: Dict) -> Dict[str, List[str]]:
        """
        Validate complete device data.
        
        Args:
            data: Device data dictionary
            
        Returns:
            Dictionary of validation errors by field
        """
        errors = {}

        # Validate name
        if "name" in data:
            is_valid, error = self.device.validate_device_name(data["name"])
            if not is_valid:
                errors["name"] = [error]

        # Validate IP
        if "ip" in data and data["ip"]:
            is_valid, error = self.network.validate_ip(data["ip"])
            if not is_valid:
                errors["ip"] = [error]

        # Validate MAC
        if "mac" in data and data["mac"]:
            is_valid, error = self.network.validate_mac(data["mac"])
            if not is_valid:
                errors["mac"] = [error]

        # Validate hostname
        if "hostname" in data and data["hostname"]:
            is_valid, error = self.network.validate_hostname(data["hostname"])
            if not is_valid:
                errors["hostname"] = [error]

        # Validate VLAN ID
        if "vlan_id" in data and data["vlan_id"] is not None:
            is_valid, error = self.network.validate_vlan_id(data["vlan_id"])
            if not is_valid:
                errors["vlan_id"] = [error]

        # Validate SNMP community
        if "snmp_community" in data and data["snmp_community"]:
            is_valid, error = self.device.validate_snmp_community(data["snmp_community"])
            if not is_valid:
                errors["snmp_community"] = [error]

        return errors

    def validate_link_data(self, data: Dict) -> Dict[str, List[str]]:
        """
        Validate complete link data.
        
        Args:
            data: Link data dictionary
            
        Returns:
            Dictionary of validation errors by field
        """
        errors = {}

        # Validate endpoints
        if "source_device_id" in data and "target_device_id" in data:
            is_valid, error = self.link.validate_link_endpoints(
                data["source_device_id"],
                data["target_device_id"]
            )
            if not is_valid:
                errors["endpoints"] = [error]

        # Validate bandwidth
        if "bandwidth" in data and data["bandwidth"] is not None:
            is_valid, error = self.link.validate_bandwidth(data["bandwidth"])
            if not is_valid:
                errors["bandwidth"] = [error]

        # Validate latency
        if "latency" in data and data["latency"] is not None:
            is_valid, error = self.link.validate_latency(data["latency"])
            if not is_valid:
                errors["latency"] = [error]

        return errors