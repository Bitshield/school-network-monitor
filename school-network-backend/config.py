"""
Application configuration settings.
"""

from pydantic_settings import BaseSettings
from pydantic import Field
from functools import lru_cache
from typing import List
import os


class Settings(BaseSettings):
    """Application configuration from environment variables."""
    
    # Application
    APP_NAME: str = "School Network Monitor"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = Field(default=False, description="Enable debug mode")
    LOG_LEVEL: str = Field(default="INFO", description="Logging level")
    ENVIRONMENT: str = Field(default="development", description="Environment: development, staging, production")
    
    # Database
    DATABASE_URL: str = Field(
        default="postgresql://postgres@localhost:5432/school_network",
        description="Database connection URL"
    )
    DATABASE_ECHO: bool = Field(default=False, description="Echo SQL queries")
    
    # Network Discovery
    DEFAULT_NETWORK_RANGE: str = Field(
        default="192.168.1.0/24",
        description="Default network range for discovery"
    )
    DISCOVERY_TIMEOUT: int = Field(default=3, ge=1, le=10, description="Discovery timeout in seconds")
    PING_TIMEOUT: int = Field(default=2, ge=1, le=5, description="Ping timeout in seconds")
    PING_COUNT: int = Field(default=3, ge=1, le=10, description="Number of ping packets")
    ARP_RETRY_COUNT: int = Field(default=2, ge=1, le=5, description="ARP retry count")
    
    # SNMP
    SNMP_COMMUNITY: str = Field(default="public", description="SNMP community string")
    SNMP_VERSION: str = Field(default="2c", description="SNMP version: 2c or 3")
    SNMP_PORT: int = Field(default=161, ge=1, le=65535, description="SNMP port")
    SNMP_TIMEOUT: int = Field(default=5, ge=1, le=30, description="SNMP timeout in seconds")
    SNMP_RETRIES: int = Field(default=3, ge=1, le=10, description="SNMP retry count")
    
    # Monitoring Intervals (seconds)
    MONITORING_INTERVAL: int = Field(default=60, ge=10, description="Device monitoring interval")
    PORT_CHECK_INTERVAL: int = Field(default=120, ge=30, description="Port check interval")
    CABLE_HEALTH_INTERVAL: int = Field(default=300, ge=60, description="Cable health check interval")
    DISCOVERY_SCAN_INTERVAL: int = Field(default=3600, ge=300, description="Network discovery interval")
    LINK_CHECK_INTERVAL: int = Field(default=60, ge=10, description="Link health check interval")
    
    # Health Thresholds
    MAX_PACKET_LOSS_PERCENT: float = Field(default=5.0, ge=0, le=100, description="Max acceptable packet loss")
    MAX_LATENCY_MS: float = Field(default=100.0, ge=0, description="Max acceptable latency in ms")
    MAX_JITTER_MS: float = Field(default=20.0, ge=0, description="Max acceptable jitter in ms")
    MIN_HEALTH_SCORE: float = Field(default=70.0, ge=0, le=100, description="Minimum acceptable health score")
    
    # Cable Validation
    MAX_CABLE_LENGTH_METERS: int = Field(default=100, ge=1, le=1000, description="Max cable length")
    MIN_LINK_SPEED_MBPS: int = Field(default=100, ge=10, description="Minimum link speed")
    REQUIRE_CABLE_CAT6_MIN: bool = Field(default=False, description="Require minimum Cat6 cable")
    
    # Topology Rules
    ALLOW_PC_TO_ROUTER_DIRECT: bool = Field(default=False, description="Allow direct PC to router connections")
    
    # WebSocket
    WS_HEARTBEAT_INTERVAL: int = Field(default=30, ge=10, description="WebSocket heartbeat interval")
    WS_HEARTBEAT_TIMEOUT: int = Field(default=60, ge=20, description="WebSocket heartbeat timeout")
    
    # API
    API_V1_PREFIX: str = "/api/v1"
    API_DOCS_URL: str = "/api/docs"
    API_REDOC_URL: str = "/api/redoc"
    API_OPENAPI_URL: str = "/api/openapi.json"
    API_TITLE: str = "School Network Monitor API"
    API_DESCRIPTION: str = "Network monitoring and management system"
    
    # Security
    SECRET_KEY: str = Field(
        default="CHANGE-THIS-IN-PRODUCTION-USE-RANDOM-STRING",
        description="Secret key for JWT tokens"
    )
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=30, ge=5, description="JWT token expiration")
    REFRESH_TOKEN_EXPIRE_DAYS: int = Field(default=7, ge=1, description="Refresh token expiration")
    
    # CORS
    ALLOWED_ORIGINS: List[str] = Field(
        default=[
            "http://localhost:3000",
            "http://localhost:4200",
            "http://localhost:8080",
        ],
        description="Allowed CORS origins"
    )
    
    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = Field(default=60, ge=1, description="API rate limit per minute")
    
    # File Upload
    MAX_UPLOAD_SIZE_MB: int = Field(default=10, ge=1, le=100, description="Max file upload size")
    
    # Pagination
    DEFAULT_PAGE_SIZE: int = Field(default=50, ge=1, le=1000, description="Default pagination size")
    MAX_PAGE_SIZE: int = Field(default=1000, ge=1, description="Maximum pagination size")
    
    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "case_sensitive": True,
        "extra": "ignore",
    }


@lru_cache()
def get_settings() -> Settings:
    """
    Get cached settings instance.
    Uses lru_cache to ensure settings are only loaded once.
    """
    return Settings()


# Global settings instance
settings = get_settings()


def validate_settings():
    """Validate critical settings on startup."""
    errors = []
    
    # Check SECRET_KEY in production
    if settings.ENVIRONMENT == "production" and settings.SECRET_KEY == "CHANGE-THIS-IN-PRODUCTION-USE-RANDOM-STRING":
        errors.append("SECRET_KEY must be changed in production!")
    
    # Check database URL
    if not settings.DATABASE_URL:
        errors.append("DATABASE_URL is required!")
    
    # Validate network range
    if not settings.DEFAULT_NETWORK_RANGE:
        errors.append("DEFAULT_NETWORK_RANGE is required!")
    
    if errors:
        raise ValueError(f"Configuration errors: {', '.join(errors)}")
    
    return True