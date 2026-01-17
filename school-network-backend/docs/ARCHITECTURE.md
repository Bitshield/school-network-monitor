# Architecture Documentation

Comprehensive guide to the School Network Monitor architecture.

## Table of Contents

1. [System Overview](#system-overview)
2. [Architecture Layers](#architecture-layers)
3. [Data Models](#data-models)
4. [API Design](#api-design)
5. [Services](#services)
6. [Database Design](#database-design)
7. [Security Architecture](#security-architecture)
8. [Monitoring Architecture](#monitoring-architecture)

## System Overview

The School Network Monitor is a modern, scalable network monitoring system built with Python FastAPI and PostgreSQL.

### High-Level Architecture
```
┌─────────────────────────────────────────────────────────────┐
│                        Client Layer                          │
│  ┌────────────┬────────────┬────────────┬────────────────┐ │
│  │  Web UI    │  Mobile    │   CLI      │  Third-party   │ │
│  │  (React)   │    App     │   Tool     │    Systems     │ │
│  └────────────┴────────────┴────────────┴────────────────┘ │
└────────────────────────┬────────────────────────────────────┘
                         │ REST API / WebSocket
┌────────────────────────┴────────────────────────────────────┐
│                      API Gateway Layer                       │
│  ┌────────────┬────────────┬────────────┬────────────────┐ │
│  │   Nginx    │   CORS     │    Rate    │  Auth/JWT      │ │
│  │   Proxy    │  Handling  │  Limiting  │   Validation   │ │
│  └────────────┴────────────┴────────────┴────────────────┘ │
└────────────────────────┬────────────────────────────────────┘
                         │
┌────────────────────────┴────────────────────────────────────┐
│                   Application Layer (FastAPI)                │
│  ┌────────────────────────────────────────────────────────┐ │
│  │                    API Endpoints (v1)                   │ │
│  │  ┌──────┬──────┬──────┬──────┬──────┬──────┬────────┐ │ │
│  │  │Devices│Ports│Links│Events│Cable │SNMP  │Stats   │ │ │
│  │  │      │     │     │      │Health│      │        │ │ │
│  │  └──────┴──────┴──────┴──────┴──────┴──────┴────────┘ │ │
│  └────────────────────────┬───────────────────────────────┘ │
│  ┌────────────────────────┴───────────────────────────────┐ │
│  │                   Service Layer                        │ │
│  │  ┌──────────┬──────────┬──────────┬────────────────┐ │ │
│  │  │Discovery │Monitoring│  SNMP    │  Cable Health  │ │ │
│  │  │ Service  │ Service  │ Service  │    Service     │ │ │
│  │  └──────────┴──────────┴──────────┴────────────────┘ │ │
│  └────────────────────────┬───────────────────────────────┘ │
│  ┌────────────────────────┴───────────────────────────────┐ │
│  │                     Data Layer                         │ │
│  │  ┌──────────┬──────────┬──────────┬────────────────┐ │ │
│  │  │ Models   │ Schemas  │Database │   Validation   │ │ │
│  │  │(ORM)     │(Pydantic)│ Session │    Logic       │ │ │
│  │  └──────────┴──────────┴──────────┴────────────────┘ │ │
│  └────────────────────────────────────────────────────────┘ │
└────────────────────────┬────────────────────────────────────┘
                         │
┌────────────────────────┴────────────────────────────────────┐
│                   Infrastructure Layer                       │
│  ┌────────────┬────────────┬────────────┬────────────────┐ │
│  │PostgreSQL  │   Redis    │  Network   │  Background    │ │
│  │  Database  │   Cache    │  Devices   │    Tasks       │ │
│  └────────────┴────────────┴────────────┴────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

## Architecture Layers

### 1. Presentation Layer

**Components:**
- Web Interface (React/Angular/Vue)
- Mobile Applications
- CLI Tools

**Responsibilities:**
- User interface rendering
- User interaction handling
- API consumption
- Real-time updates via WebSocket

### 2. API Layer (FastAPI)

**Structure:**
```
api/
├── __init__.py
├── deps.py              # Shared dependencies
└── v1/                  # API version 1
    ├── router.py        # Main router
    ├── devices.py       # Device endpoints
    ├── ports.py         # Port endpoints
    ├── links.py         # Link endpoints
    ├── events.py        # Event endpoints
    ├── cable_health.py  # Cable health endpoints
    ├── monitoring.py    # Monitoring endpoints
    ├── discovery.py     # Discovery endpoints
    ├── snmp.py          # SNMP endpoints
    ├── statistics.py    # Statistics endpoints
    └── validation.py    # Validation endpoints
```

**Responsibilities:**
- HTTP request handling
- Input validation
- Response formatting
- Authentication/Authorization
- Rate limiting

### 3. Service Layer

**Services:**

#### NetworkDiscovery Service
```python
class NetworkDiscovery:
    - arp_scan()          # ARP discovery
    - icmp_ping()         # Ping sweep
    - scan_network()      # Full network scan
    - classify_device()   # Device classification
```

#### MonitoringService
```python
class MonitoringService:
    - check_devices()     # Device health checks
    - check_links()       # Link monitoring
    - check_ports()       # Port status
    - run_cycle()         # Monitoring cycle
```

#### SNMPService
```python
class SNMPService:
    - get_device_info()   # System information
    - get_interfaces()    # Interface data
    - query_oid()         # OID queries
    - walk_oid()          # OID walking
```

#### CableHealthService
```python
class CableHealthService:
    - test_link()         # Link testing
    - analyze_health()    # Health analysis
    - get_history()       # Historical data
```

### 4. Data Layer

**Models (SQLAlchemy ORM):**
```
models/
├── device.py           # Device model
├── port.py            # Port model
├── link.py            # Link model
├── event.py           # Event model
└── cable_health.py    # Cable health model
```

**Schemas (Pydantic):**
```
schemas/
├── device.py          # Device schemas
├── port.py           # Port schemas
├── link.py           # Link schemas
├── event.py          # Event schemas
└── cable_health.py   # Cable health schemas
```

## Data Models

### Entity Relationship Diagram
```
┌──────────────┐
│   Device     │
│──────────────│
│ id (PK)      │◄─────┐
│ name         │      │
│ device_type  │      │
│ ip           │      │
│ mac          │      │
│ status       │      │
└──────────────┘      │
       │              │
       │ 1:N          │ N:1
       ▼              │
┌──────────────┐      │
│    Port      │      │
│──────────────│      │
│ id (PK)      │      │
│ device_id(FK)│──────┘
│ port_name    │
│ status       │
│ statistics   │
└──────────────┘
       │
       │ 1:N
       ▼
┌──────────────────────┐
│       Link           │
│──────────────────────│
│ id (PK)              │
│ source_device_id(FK) │───┐
│ target_device_id(FK) │───┤
│ source_port_id (FK)  │   │
│ target_port_id (FK)  │   │
│ status               │   │
│ performance_metrics  │   │
└──────────────────────┘   │
       │                   │
       │ 1:N               │
       ▼                   │
┌──────────────────────┐   │
│  CableHealthMetrics  │   │
│──────────────────────│   │
│ id (PK)              │   │
│ link_id (FK)         │───┘
│ health_score         │
│ signal_quality       │
│ metrics              │
└──────────────────────┘

┌──────────────┐
│    Event     │
│──────────────│
│ id (PK)      │
│ device_id(FK)│───┐
│ port_id (FK) │───┤ Optional FK
│ link_id (FK) │───┘
│ event_type   │
│ severity     │
│ message      │
└──────────────┘
```

### Device Model
```python
class Device:
    id: str (PK)
    name: str
    device_type: DeviceTypeEnum
    ip: str (unique)
    mac: str (unique)
    hostname: str
    location: str
    status: DeviceStatusEnum
    last_seen: datetime
    is_monitored: bool
    
    # SNMP
    snmp_enabled: bool
    snmp_community: str
    snmp_version: str
    
    # Position
    position_x: float
    position_y: float
    
    # Relationships
    ports: List[Port]
    from_links: List[Link]
    to_links: List[Link]
    events: List[Event]
```

### Port Model
```python
class Port:
    id: str (PK)
    device_id: str (FK)
    name: str
    port_number: int
    port_type: PortTypeEnum
    status: PortStatusEnum
    
    # Configuration
    speed_mbps: float
    vlan_id: int
    is_trunk: bool
    
    # Statistics
    rx_bytes: int
    tx_bytes: int
    rx_errors: int
    tx_errors: int
    
    # Relationships
    device: Device
    source_links: List[Link]
    target_links: List[Link]
```

### Link Model
```python
class Link:
    id: str (PK)
    source_device_id: str (FK)
    target_device_id: str (FK)
    source_port_id: str (FK, nullable)
    target_port_id: str (FK, nullable)
    
    link_type: LinkTypeEnum
    status: LinkStatusEnum
    
    # Performance
    bandwidth: int
    latency: float
    packet_loss: float
    jitter: float
    
    # Relationships
    source_device: Device
    target_device: Device
    health_metrics: List[CableHealthMetrics]
```

## API Design

### RESTful Principles

#### Resource Naming
```
GET    /api/v1/devices          # List devices
GET    /api/v1/devices/{id}     # Get device
POST   /api/v1/devices          # Create device
PUT    /api/v1/devices/{id}     # Update device
DELETE /api/v1/devices/{id}     # Delete device
```

#### Status Codes
- `200 OK` - Successful GET/PUT
- `201 Created` - Successful POST
- `204 No Content` - Successful DELETE
- `400 Bad Request` - Invalid input
- `401 Unauthorized` - Authentication required
- `403 Forbidden` - Insufficient permissions
- `404 Not Found` - Resource not found
- `422 Unprocessable Entity` - Validation error
- `429 Too Many Requests` - Rate limit exceeded
- `500 Internal Server Error` - Server error

#### Response Format
```json
{
  "id": "device-123",
  "name": "Core Router 1",
  "device_type": "ROUTER",
  "status": "UP",
  "created_at": "2025-01-15T10:00:00Z"
}
```

#### Error Format
```json
{
  "detail": "Device not found",
  "status_code": 404
}
```

### Pagination
```
GET /api/v1/devices?page=1&page_size=50
```

Response includes:
```json
{
  "items": [...],
  "total": 150,
  "page": 1,
  "page_size": 50,
  "total_pages": 3
}
```

### Filtering
```
GET /api/v1/devices?status=UP&device_type=ROUTER
```

### Sorting
```
GET /api/v1/devices?sort_by=name&sort_order=asc
```

## Services

### Base Service Pattern
```python
class BaseService(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    def __init__(self, model: Type[ModelType], db: AsyncSession):
        self.model = model
        self.db = db
    
    async def get(self, id: str) -> Optional[ModelType]
    async def get_multi(self, skip: int, limit: int) -> List[ModelType]
    async def create(self, obj_in: CreateSchemaType) -> ModelType
    async def update(self, id: str, obj_in: UpdateSchemaType) -> ModelType
    async def delete(self, id: str) -> bool
```

### Service Dependencies

Services use dependency injection:
```python
from api.deps import get_db

@router.get("/devices")
async def get_devices(db: AsyncSession = Depends(get_db)):
    service = DeviceService(db)
    return await service.get_all()
```

## Database Design

### Connection Pool
```python
engine = create_async_engine(
    DATABASE_URL,
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True,
    pool_recycle=3600
)
```

### Migrations (Alembic)
```bash
# Create migration
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head

# Rollback
alembic downgrade -1
```

### Indexes

Critical indexes for performance:
```sql
CREATE INDEX idx_devices_status ON devices(status);
CREATE INDEX idx_devices_type ON devices(device_type);
CREATE INDEX idx_links_source ON links(source_device_id);
CREATE INDEX idx_events_created ON events(created_at);
```

## Security Architecture

### Authentication Flow
```
1. User -> POST /auth/login (credentials)
2. Server validates credentials
3. Server generates JWT token
4. Server -> User (access_token, refresh_token)
5. User includes token in Authorization header
6. Server validates token on each request
```

### JWT Token Structure
```json
{
  "sub": "user-123",
  "username": "admin",
  "is_admin": true,
  "exp": 1642345678,
  "iat": 1642342078
}
```

### Password Security

- Hashing: bcrypt with salt
- Minimum length: 8 characters
- Complexity requirements configurable

### API Key Security

- Optional API key authentication
- Keys stored as hashed values
- Rate limiting per key

## Monitoring Architecture

### Monitoring Cycle
```python
while True:
    1. Check all monitored devices
    2. Test all active links
    3. Collect port statistics
    4. Analyze cable health
    5. Generate events for issues
    6. Sleep for interval
```

### Event Generation
```python
if device.status changes:
    create_event(
        type="DEVICE_DOWN",
        severity="HIGH",
        device_id=device.id
    )
```

### Background Tasks

Using asyncio for concurrent monitoring:
```python
async def start_monitoring():
    tasks = [
        monitor_devices(),
        monitor_links(),
        collect_statistics()
    ]
    await asyncio.gather(*tasks)
```

## Performance Considerations

### Database Query Optimization
- Use indexes on frequently queried columns
- Implement pagination for large result sets
- Use select/join loading for relationships

### Caching Strategy
- Redis for session data
- In-memory cache for static data
- TTL-based invalidation

### Async Processing
- All I/O operations are async
- Concurrent monitoring tasks
- Background job processing

## Scalability

### Horizontal Scaling
- Stateless API servers
- Load balancer distribution
- Session storage in Redis

### Vertical Scaling
- Database connection pooling
- Efficient query patterns
- Resource monitoring

---

**Architecture Version:** 1.0  
**Last Updated:** January 2025