"""
Custom exceptions for the application.
"""

from typing import Any, Optional, Dict
from fastapi import HTTPException, status


class NetworkMonitorException(Exception):
    """Base exception for all custom exceptions."""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        self.message = message
        self.details = details or {}
        super().__init__(self.message)


class DatabaseException(NetworkMonitorException):
    """Database operation exceptions."""
    pass


class ValidationException(NetworkMonitorException):
    """Data validation exceptions."""
    pass


class DeviceException(NetworkMonitorException):
    """Device-related exceptions."""
    pass


class DeviceNotFoundException(DeviceException):
    """Device not found in database."""
    
    def __init__(self, device_id: str):
        super().__init__(
            message=f"Device with ID '{device_id}' not found",
            details={"device_id": device_id}
        )


class DeviceAlreadyExistsException(DeviceException):
    """Device already exists."""
    
    def __init__(self, identifier: str, identifier_type: str = "IP"):
        super().__init__(
            message=f"Device with {identifier_type} '{identifier}' already exists",
            details={"identifier": identifier, "type": identifier_type}
        )


class PortException(NetworkMonitorException):
    """Port-related exceptions."""
    pass


class PortNotFoundException(PortException):
    """Port not found in database."""
    
    def __init__(self, port_id: str):
        super().__init__(
            message=f"Port with ID '{port_id}' not found",
            details={"port_id": port_id}
        )


class LinkException(NetworkMonitorException):
    """Link-related exceptions."""
    pass


class LinkNotFoundException(LinkException):
    """Link not found in database."""
    
    def __init__(self, link_id: str):
        super().__init__(
            message=f"Link with ID '{link_id}' not found",
            details={"link_id": link_id}
        )


class InvalidLinkException(LinkException):
    """Invalid link configuration."""
    
    def __init__(self, reason: str):
        super().__init__(
            message=f"Invalid link configuration: {reason}",
            details={"reason": reason}
        )


class EventException(NetworkMonitorException):
    """Event-related exceptions."""
    pass


class EventNotFoundException(EventException):
    """Event not found in database."""
    
    def __init__(self, event_id: str):
        super().__init__(
            message=f"Event with ID '{event_id}' not found",
            details={"event_id": event_id}
        )


class NetworkException(NetworkMonitorException):
    """Network operation exceptions."""
    pass


class NetworkDiscoveryException(NetworkException):
    """Network discovery failures."""
    pass


class SNMPException(NetworkException):
    """SNMP operation exceptions."""
    
    def __init__(self, host: str, message: str):
        super().__init__(
            message=f"SNMP error for host {host}: {message}",
            details={"host": host}
        )


class MonitoringException(NetworkMonitorException):
    """Monitoring service exceptions."""
    pass


class ConfigurationException(NetworkMonitorException):
    """Configuration-related exceptions."""
    pass


class AuthenticationException(NetworkMonitorException):
    """Authentication failures."""
    pass


class AuthorizationException(NetworkMonitorException):
    """Authorization failures."""
    pass


# HTTP Exception Helpers
def raise_not_found(resource: str, identifier: str) -> None:
    """Raise HTTP 404 Not Found exception."""
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"{resource} with identifier '{identifier}' not found"
    )


def raise_bad_request(message: str, details: Optional[Dict] = None) -> None:
    """Raise HTTP 400 Bad Request exception."""
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail={"message": message, "details": details or {}}
    )


def raise_conflict(message: str, details: Optional[Dict] = None) -> None:
    """Raise HTTP 409 Conflict exception."""
    raise HTTPException(
        status_code=status.HTTP_409_CONFLICT,
        detail={"message": message, "details": details or {}}
    )


def raise_unauthorized(message: str = "Unauthorized") -> None:
    """Raise HTTP 401 Unauthorized exception."""
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail=message,
        headers={"WWW-Authenticate": "Bearer"},
    )


def raise_forbidden(message: str = "Forbidden") -> None:
    """Raise HTTP 403 Forbidden exception."""
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail=message
    )


def raise_unprocessable_entity(message: str, errors: Optional[list] = None) -> None:
    """Raise HTTP 422 Unprocessable Entity exception."""
    raise HTTPException(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        detail={"message": message, "errors": errors or []}
    )


def raise_internal_error(message: str = "Internal server error") -> None:
    """Raise HTTP 500 Internal Server Error exception."""
    raise HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail=message
    )


def raise_service_unavailable(message: str = "Service temporarily unavailable") -> None:
    """Raise HTTP 503 Service Unavailable exception."""
    raise HTTPException(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        detail=message
    )