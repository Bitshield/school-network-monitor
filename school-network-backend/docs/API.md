# 📚 API Documentation

Complete REST API reference for School Network Monitor.

## 📋 Table of Contents

1. [Overview](#-overview)
2. [Authentication](#-authentication)
3. [Common Patterns](#-common-patterns)
4. [Devices API](#-devices-api)
5. [Ports API](#-ports-api)
6. [Links API](#-links-api)
7. [Events API](#-events-api)
8. [Cable Health API](#-cable-health-api)
9. [Monitoring API](#-monitoring-api)
10. [Discovery API](#-discovery-api)
11. [SNMP API](#-snmp-api)
12. [Statistics API](#-statistics-api)
13. [Validation API](#-validation-api)
14. [Error Handling](#-error-handling)
15. [Rate Limiting](#-rate-limiting)

---

## 🌐 Overview

### Base URL
```
Production:  https://network.yourdomain.com/api/v1
Development: http://localhost:8000/api/v1
```

### API Version

Current Version: **v1**

### Content Type

All requests and responses use JSON:
```
Content-Type: application/json
```

### Interactive Documentation

- **Swagger UI:** `/api/docs`
- **ReDoc:** `/api/redoc`
- **OpenAPI Spec:** `/api/openapi.json`

---

## 🔐 Authentication

### JWT Token Authentication

Most endpoints require JWT token authentication.

#### Request Headers
```http
Authorization: Bearer <your-jwt-token>
```

#### Token Structure
```json
{
  "sub": "user-123",
  "username": "admin",
  "is_admin": true,
  "exp": 1705484400,
  "iat": 1705480800,
  "type": "access"
}
```

#### Token Expiration

| Token Type | Expiration |
|------------|-----------|
| Access Token | 30 minutes |
| Refresh Token | 7 days |

---

## 🔄 Common Patterns

### Pagination

#### Request Parameters

| Parameter | Type | Default | Max | Description |
|-----------|------|---------|-----|-------------|
| `page` | integer | 1 | - | Page number (1-indexed) |
| `page_size` | integer | 50 | 1000 | Items per page |

#### Example Request
```http
GET /api/v1/devices?page=2&page_size=25
```

#### Response Format
```json
[
  {
    "id": "dev-001",
    "name": "Device 1"
  },
  {
    "id": "dev-002",
    "name": "Device 2"
  }
]
```

### Filtering

#### Common Filter Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `search` | string | Search across multiple fields |
| `status` | enum | Filter by status |
| `device_type` | enum | Filter by device type |
| `sort_by` | string | Field to sort by |
| `sort_order` | enum | `asc` or `desc` |

#### Example
```http
GET /api/v1/devices?status=UP&device_type=ROUTER&sort_by=name&sort_order=asc
```

### Date/Time Filtering
```http
GET /api/v1/events?start_date=2025-01-01T00:00:00Z&end_date=2025-01-17T23:59:59Z
```

### Response Status Codes

| Code | Status | Description |
|------|--------|-------------|
| 200 | OK | Successful GET/PUT request |
| 201 | Created | Successful POST request |
| 204 | No Content | Successful DELETE request |
| 400 | Bad Request | Invalid request parameters |
| 401 | Unauthorized | Authentication required |
| 403 | Forbidden | Insufficient permissions |
| 404 | Not Found | Resource not found |
| 409 | Conflict | Resource already exists |
| 422 | Unprocessable Entity | Validation error |
| 429 | Too Many Requests | Rate limit exceeded |
| 500 | Internal Server Error | Server error |

---

## 🖥️ Devices API

### Device Object
```json
{
  "id": "dev-001",
  "name": "Core Router 1",
  "device_type": "ROUTER",
  "ip": "192.168.1.1",
  "mac": "00:1A:2B:3C:4D:01",
  "hostname": "core-router-01",
  "location": "Server Room A",
  "description": "Main core router for building A",
  "status": "UP",
  "last_seen": "2025-01-17T10:30:00Z",
  "is_monitored": true,
  "vlan_id": 1,
  "subnet": "192.168.1.0/24",
  "snmp_enabled": true,
  "snmp_community": "public",
  "snmp_version": "2c",
  "position_x": 400.0,
  "position_y": 100.0,
  "created_at": "2025-01-01T00:00:00Z",
  "updated_at": "2025-01-17T10:30:00Z"
}
```

#### Device Types

| Value | Description |
|-------|-------------|
| `ROUTER` | Network router |
| `SWITCH` | Network switch |
| `SERVER` | Server |
| `PC` | Personal computer |
| `AP` | Access point |
| `PRINTER` | Network printer |
| `CAMERA` | IP camera |
| `UNKNOWN` | Unknown device type |

#### Device Status

| Value | Description |
|-------|-------------|
| `UP` | Device is online |
| `DOWN` | Device is offline |
| `UNREACHABLE` | Device cannot be reached |
| `UNKNOWN` | Status unknown |

### List Devices
```http
GET /api/v1/devices
```

#### Query Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `page` | integer | Page number |
| `page_size` | integer | Items per page |
| `search` | string | Search by name, IP, MAC, hostname |
| `status` | enum | Filter by status |
| `device_type` | enum | Filter by device type |
| `is_monitored` | boolean | Filter by monitoring status |
| `sort_by` | string | Sort field |
| `sort_order` | string | `asc` or `desc` |

#### Example Request
```bash
curl -X GET "http://localhost:8000/api/v1/devices?status=UP&device_type=ROUTER&page=1&page_size=20" \
  -H "Authorization: Bearer <token>"
```

#### Example Response
```json
[
  {
    "id": "dev-001",
    "name": "Core Router 1",
    "device_type": "ROUTER",
    "ip": "192.168.1.1",
    "mac": "00:1A:2B:3C:4D:01",
    "status": "UP",
    "last_seen": "2025-01-17T10:30:00Z",
    "is_monitored": true,
    "created_at": "2025-01-01T00:00:00Z",
    "updated_at": "2025-01-17T10:30:00Z"
  },
  {
    "id": "dev-002",
    "name": "Core Router 2",
    "device_type": "ROUTER",
    "ip": "192.168.1.2",
    "mac": "00:1A:2B:3C:4D:02",
    "status": "UP",
    "last_seen": "2025-01-17T10:30:00Z",
    "is_monitored": true,
    "created_at": "2025-01-01T00:00:00Z",
    "updated_at": "2025-01-17T10:30:00Z"
  }
]
```

### Get Device Count
```http
GET /api/v1/devices/count
```

#### Query Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `status` | enum | Filter by status |
| `device_type` | enum | Filter by device type |

#### Example Response
```json
{
  "count": 42
}
```

### Get Single Device
```http
GET /api/v1/devices/{device_id}
```

#### Path Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `device_id` | string | Device ID |

#### Example Request
```bash
curl -X GET "http://localhost:8000/api/v1/devices/dev-001" \
  -H "Authorization: Bearer <token>"
```

#### Example Response
```json
{
  "id": "dev-001",
  "name": "Core Router 1",
  "device_type": "ROUTER",
  "ip": "192.168.1.1",
  "mac": "00:1A:2B:3C:4D:01",
  "hostname": "core-router-01",
  "location": "Server Room A",
  "description": "Main core router",
  "status": "UP",
  "last_seen": "2025-01-17T10:30:00Z",
  "is_monitored": true,
  "vlan_id": 1,
  "snmp_enabled": true,
  "position_x": 400.0,
  "position_y": 100.0,
  "created_at": "2025-01-01T00:00:00Z",
  "updated_at": "2025-01-17T10:30:00Z",
  "ports": [],
  "from_links": [],
  "to_links": []
}
```

### Create Device
```http
POST /api/v1/devices
```

#### Request Body
```json
{
  "name": "New Switch",
  "device_type": "SWITCH",
  "ip": "192.168.1.10",
  "mac": "00:1A:2B:3C:4D:10",
  "hostname": "switch-01",
  "location": "Floor 2",
  "description": "Access switch for floor 2",
  "vlan_id": 10,
  "snmp_enabled": true,
  "snmp_community": "public",
  "position_x": 250.0,
  "position_y": 300.0
}
```

#### Required Fields

- `name` (string)
- `device_type` (enum)

#### Example Request
```bash
curl -X POST "http://localhost:8000/api/v1/devices" \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "New Switch",
    "device_type": "SWITCH",
    "ip": "192.168.1.10",
    "mac": "00:1A:2B:3C:4D:10"
  }'
```

#### Example Response (201 Created)
```json
{
  "id": "dev-new",
  "name": "New Switch",
  "device_type": "SWITCH",
  "ip": "192.168.1.10",
  "mac": "00:1A:2B:3C:4D:10",
  "status": "UNKNOWN",
  "is_monitored": true,
  "created_at": "2025-01-17T11:00:00Z",
  "updated_at": "2025-01-17T11:00:00Z"
}
```

### Update Device
```http
PUT /api/v1/devices/{device_id}
```

#### Request Body (all fields optional)
```json
{
  "name": "Updated Switch Name",
  "location": "Floor 3",
  "description": "Moved to floor 3",
  "status": "UP",
  "position_x": 300.0,
  "position_y": 400.0
}
```

#### Example Request
```bash
curl -X PUT "http://localhost:8000/api/v1/devices/dev-001" \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Updated Router Name",
    "location": "Server Room B"
  }'
```

### Delete Device
```http
DELETE /api/v1/devices/{device_id}
```

#### Example Request
```bash
curl -X DELETE "http://localhost:8000/api/v1/devices/dev-001" \
  -H "Authorization: Bearer <token>"
```

#### Response
```
204 No Content
```

### Ping Device
```http
POST /api/v1/devices/{device_id}/ping
```

Test device connectivity via ICMP ping.

#### Example Response
```json
{
  "device_id": "dev-001",
  "device_name": "Core Router 1",
  "ip": "192.168.1.1",
  "is_alive": true,
  "status": "UP",
  "latency_ms": 2.5,
  "packet_loss": 0.0,
  "status_changed": false,
  "checked_at": "2025-01-17T11:00:00Z"
}
```

### Get Device Ports
```http
GET /api/v1/devices/{device_id}/ports
```

Get all ports for a specific device.

#### Example Response
```json
[
  {
    "id": "port-001",
    "device_id": "dev-001",
    "name": "GigabitEthernet0/0",
    "port_number": 1,
    "port_name": "Gi0/0",
    "status": "UP",
    "speed_mbps": 1000.0
  }
]
```

### Get Device Links
```http
GET /api/v1/devices/{device_id}/links
```

Get all links connected to a device.

### Get Device Events
```http
GET /api/v1/devices/{device_id}/events
```

#### Query Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `limit` | integer | 50 | Maximum events to return |

---

## 🔌 Ports API

### Port Object
```json
{
  "id": "port-001",
  "device_id": "dev-001",
  "name": "GigabitEthernet0/0",
  "port_number": 1,
  "port_name": "Gi0/0",
  "port_type": "ETHERNET",
  "status": "UP",
  "is_up": true,
  "speed_mbps": 1000.0,
  "max_speed_mbps": 1000.0,
  "mtu": 1500,
  "duplex": "Full",
  "vlan_id": 1,
  "is_trunk": true,
  "allowed_vlans": "1,10,20,30",
  "native_vlan": 1,
  "mac_address": "00:1A:2B:3C:4D:01",
  "rx_bytes": 1234567890,
  "tx_bytes": 9876543210,
  "rx_packets": 123456,
  "tx_packets": 654321,
  "rx_errors": 0,
  "tx_errors": 0,
  "description": "Uplink port",
  "created_at": "2025-01-01T00:00:00Z",
  "updated_at": "2025-01-17T10:30:00Z",
  "last_seen": "2025-01-17T10:30:00Z"
}
```

#### Port Types

| Value | Description |
|-------|-------------|
| `ETHERNET` | Ethernet port |
| `FIBER` | Fiber optic port |
| `SFP` | SFP port |
| `SFP+` | SFP+ port |
| `QSFP` | QSFP port |
| `VIRTUAL` | Virtual port |
| `UNKNOWN` | Unknown type |

#### Port Status

| Value | Description |
|-------|-------------|
| `UP` | Port is up |
| `DOWN` | Port is down |
| `DISABLED` | Port is disabled |
| `ERROR` | Port has errors |
| `UNKNOWN` | Status unknown |

### List Ports
```http
GET /api/v1/ports
```

#### Query Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `page` | integer | Page number |
| `page_size` | integer | Items per page |
| `device_id` | string | Filter by device |
| `status` | enum | Filter by status |

#### Example Request
```bash
curl -X GET "http://localhost:8000/api/v1/ports?device_id=dev-001&status=UP" \
  -H "Authorization: Bearer <token>"
```

### Get Single Port
```http
GET /api/v1/ports/{port_id}
```

### Create Port
```http
POST /api/v1/ports
```

#### Request Body
```json
{
  "device_id": "dev-001",
  "name": "GigabitEthernet0/1",
  "port_number": 2,
  "port_type": "ETHERNET",
  "speed": "1G",
  "vlan_id": 10,
  "description": "Access port for VLAN 10"
}
```

#### Required Fields

- `device_id` (string)
- `name` (string)
- `port_number` (integer, >= 1)

### Update Port
```http
PUT /api/v1/ports/{port_id}
```

### Delete Port
```http
DELETE /api/v1/ports/{port_id}
```

### Get Port Statistics
```http
GET /api/v1/ports/{port_id}/statistics
```

#### Example Response
```json
{
  "port_id": "port-001",
  "device_id": "dev-001",
  "port_name": "Gi0/0",
  "status": "UP",
  "statistics": {
    "rx_bytes": 1234567890,
    "tx_bytes": 9876543210,
    "rx_packets": 123456,
    "tx_packets": 654321,
    "rx_errors": 0,
    "tx_errors": 0,
    "rx_dropped": 0,
    "tx_dropped": 0,
    "crc_errors": 0,
    "frame_errors": 0,
    "collision_count": 0
  },
  "last_check": "2025-01-17T10:30:00Z"
}
```

---

## 🔗 Links API

### Link Object
```json
{
  "id": "link-001",
  "source_device_id": "dev-001",
  "target_device_id": "dev-002",
  "source_port_id": "port-001",
  "target_port_id": "port-002",
  "link_type": "PHYSICAL",
  "status": "UP",
  "bandwidth": 1000,
  "speed_mbps": 1000.0,
  "duplex": "Full",
  "utilization": 45.5,
  "packet_loss": 0.01,
  "latency": 0.5,
  "jitter": 0.1,
  "cost": 10,
  "description": "Core link between routers",
  "created_at": "2025-01-01T00:00:00Z",
  "updated_at": "2025-01-17T10:30:00Z",
  "last_seen": "2025-01-17T10:30:00Z"
}
```

#### Link Types

| Value | Description |
|-------|-------------|
| `PHYSICAL` | Physical connection |
| `LOGICAL` | Logical connection |
| `VIRTUAL` | Virtual connection |
| `UNKNOWN` | Unknown type |

#### Link Status

| Value | Description |
|-------|-------------|
| `UP` | Link is up |
| `DOWN` | Link is down |
| `DEGRADED` | Link is degraded |
| `UNKNOWN` | Status unknown |

### List Links
```http
GET /api/v1/links
```

#### Query Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `page` | integer | Page number |
| `page_size` | integer | Items per page |
| `status` | enum | Filter by status |
| `device_id` | string | Filter by device (source or target) |

### Get Single Link
```http
GET /api/v1/links/{link_id}
```

### Create Link
```http
POST /api/v1/links
```

#### Request Body
```json
{
  "source_device_id": "dev-001",
  "target_device_id": "dev-002",
  "source_port_id": "port-001",
  "target_port_id": "port-002",
  "link_type": "PHYSICAL",
  "bandwidth": 1000,
  "description": "Primary uplink"
}
```

#### Required Fields

- `source_device_id` (string)
- `target_device_id` (string)

#### Validation Rules

- Source and target devices must be different
- Link must not already exist between the same devices

### Update Link
```http
PUT /api/v1/links/{link_id}
```

### Delete Link
```http
DELETE /api/v1/links/{link_id}
```

### Test Link Health
```http
POST /api/v1/links/{link_id}/test
```

Run a health test on the link.

#### Example Response
```json
{
  "link_id": "link-001",
  "test_results": {
    "target_ip": "192.168.1.2",
    "is_reachable": true,
    "latency_min_ms": 0.4,
    "latency_avg_ms": 0.5,
    "latency_max_ms": 0.7,
    "packet_loss_percent": 0.0,
    "jitter_ms": 0.3,
    "health_score": 98.5,
    "status": "EXCELLENT"
  },
  "recommendations": [
    "✅ Link health is EXCELLENT. No issues detected."
  ],
  "timestamp": "2025-01-17T11:00:00Z"
}
```

### Get Link Health History
```http
GET /api/v1/links/{link_id}/health-history
```

#### Query Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `hours` | integer | 24 | Hours of history |

---

## 📋 Events API

### Event Object
```json
{
  "id": "event-001",
  "event_type": "DEVICE_DOWN",
  "severity": "HIGH",
  "device_id": "dev-001",
  "port_id": null,
  "link_id": null,
  "message": "Device Core Router 1 went offline",
  "details": {
    "old_status": "UP",
    "new_status": "DOWN",
    "ip": "192.168.1.1"
  },
  "source": "monitoring_service",
  "acknowledged": false,
  "acknowledged_by": null,
  "acknowledged_at": null,
  "notes": null,
  "resolved": false,
  "resolved_by": null,
  "resolved_at": null,
  "occurrence_count": 1,
  "first_occurred_at": "2025-01-17T10:00:00Z",
  "last_occurred_at": "2025-01-17T10:00:00Z",
  "created_at": "2025-01-17T10:00:00Z",
  "updated_at": "2025-01-17T10:00:00Z"
}
```

#### Event Types

| Value | Description |
|-------|-------------|
| `DEVICE_UP` | Device came online |
| `DEVICE_DOWN` | Device went offline |
| `DEVICE_DISCOVERED` | New device discovered |
| `DEVICE_REMOVED` | Device removed |
| `PORT_UP` | Port came up |
| `PORT_DOWN` | Port went down |
| `LINK_UP` | Link came up |
| `LINK_DOWN` | Link went down |
| `LINK_DEGRADED` | Link quality degraded |
| `HIGH_LATENCY` | High latency detected |
| `HIGH_PACKET_LOSS` | High packet loss |
| `CABLE_HEALTH_DEGRADED` | Cable health degraded |
| `CABLE_HEALTH_CRITICAL` | Cable health critical |
| `SCAN_COMPLETED` | Network scan completed |
| `CONFIGURATION_CHANGE` | Configuration changed |

#### Severity Levels

| Value | Description | Color |
|-------|-------------|-------|
| `CRITICAL` | Critical - immediate action required | 🔴 Red |
| `HIGH` | High - action required soon | 🟠 Orange |
| `MEDIUM` | Medium - should be addressed | 🟡 Yellow |
| `LOW` | Low - minor issue | 🔵 Blue |
| `INFO` | Information only | ⚪ White |

### List Events
```http
GET /api/v1/events
```

#### Query Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `page` | integer | Page number |
| `page_size` | integer | Items per page |
| `event_type` | enum | Filter by event type |
| `severity` | enum | Filter by severity |
| `device_id` | string | Filter by device |
| `acknowledged` | boolean | Filter by acknowledgement |
| `resolved` | boolean | Filter by resolution |
| `start_date` | datetime | Events after this date |
| `end_date` | datetime | Events before this date |

#### Example Request
```bash
curl -X GET "http://localhost:8000/api/v1/events?severity=CRITICAL&acknowledged=false&limit=10" \
  -H "Authorization: Bearer <token>"
```

### Get Unacknowledged Events
```http
GET /api/v1/events/unacknowledged
```

Get all unacknowledged events, ordered by severity.

#### Query Parameters

| Parameter | Type | Default | Max | Description |
|-----------|------|---------|-----|-------------|
| `limit` | integer | 100 | 500 | Maximum events |

### Get Critical Events
```http
GET /api/v1/events/critical
```

Get critical events from the last N hours.

#### Query Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `hours` | integer | 24 | Hours to look back |

### Get Events Summary
```http
GET /api/v1/events/summary
```

Get summary statistics of events.

#### Example Response
```json
{
  "total_events": 156,
  "unacknowledged": 12,
  "unresolved": 45,
  "by_severity": {
    "CRITICAL": 3,
    "HIGH": 8,
    "MEDIUM": 25,
    "LOW": 67,
    "INFO": 53
  },
  "by_type": {
    "DEVICE_DOWN": 5,
    "LINK_DEGRADED": 8,
    "HIGH_LATENCY": 12,
    "PORT_DOWN": 3
  },
  "time_range_hours": 24
}
```

### Get Single Event
```http
GET /api/v1/events/{event_id}
```

### Create Event
```http
POST /api/v1/events
```

#### Request Body
```json
{
  "event_type": "DEVICE_DOWN",
  "severity": "HIGH",
  "device_id": "dev-001",
  "message": "Device went offline unexpectedly",
  "details": {
    "reason": "network_timeout",
    "last_successful_ping": "2025-01-17T10:00:00Z"
  },
  "source": "monitoring_service"
}
```

### Acknowledge Event
```http
PATCH /api/v1/events/{event_id}/acknowledge
```

#### Request Body
```json
{
  "acknowledged_by": "admin",
  "notes": "Investigating the issue"
}
```

#### Example Response
```json
{
  "message": "Event acknowledged successfully",
  "event_id": "event-001",
  "acknowledged_by": "admin",
  "acknowledged_at": "2025-01-17T11:00:00Z"
}
```

### Resolve Event
```http
PATCH /api/v1/events/{event_id}/resolve
```

#### Request Body
```json
{
  "resolved_by": "admin",
  "resolution_notes": "Device power cycled and came back online"
}
```

### Bulk Acknowledge Events
```http
POST /api/v1/events/bulk-acknowledge
```

#### Request Body
```json
{
  "event_ids": ["event-001", "event-002", "event-003"],
  "acknowledged_by": "admin",
  "notes": "Mass acknowledgement after maintenance"
}
```

#### Example Response
```json
{
  "message": "Acknowledged 3 events",
  "acknowledged_count": 3,
  "total_events": 3
}
```

### Delete Event
```http
DELETE /api/v1/events/{event_id}
```

---

## 🔬 Cable Health API

### Cable Health Metric Object
```json
{
  "id": "health-001",
  "link_id": "link-001",
  "cable_type": "CAT6A",
  "status": "EXCELLENT",
  "length": 15.5,
  "signal_strength": -45.0,
  "signal_quality": 98,
  "noise_level": -85.0,
  "snr": 40.0,
  "attenuation": 2.5,
  "impedance": 100.0,
  "latency_ms": 0.5,
  "packet_loss_percent": 0.01,
  "jitter_ms": 0.1,
  "health_score": 98.5,
  "test_date": "2025-01-17T10:00:00Z",
  "created_at": "2025-01-17T10:00:00Z"
}
```

#### Cable Types

| Value | Description | Speed |
|-------|-------------|-------|
| `CAT5` | Category 5 | 100 Mbps |
| `CAT5E` | Category 5e | 1 Gbps |
| `CAT6` | Category 6 | 10 Gbps |
| `CAT6A` | Category 6a | 10 Gbps |
| `CAT7` | Category 7 | 10 Gbps |
| `FIBER_SM` | Single-mode fiber | 100+ Gbps |
| `FIBER_MM` | Multi-mode fiber | 40 Gbps |
| `COAX` | Coaxial cable | 1 Gbps |

#### Health Status

| Value | Score Range | Indicator |
|-------|-------------|-----------|
| `EXCELLENT` | 90-100 | 🟢 Green |
| `GOOD` | 80-89 | 🟢 Green |
| `FAIR` | 60-79 | 🟡 Yellow |
| `POOR` | 40-59 | 🟠 Orange |
| `CRITICAL` | 0-39 | 🔴 Red |

### List Cable Health Metrics
```http
GET /api/v1/cable-health
```

#### Query Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `page` | integer | Page number |
| `page_size` | integer | Items per page |
| `link_id` | string | Filter by link |
| `status` | enum | Filter by status |

### Get Unhealthy Cables
```http
GET /api/v1/cable-health/unhealthy
```

Get cables with health score below threshold.

#### Query Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `threshold` | float | 70.0 | Health score threshold (0-100) |

#### Example Response
```json
{
  "threshold": 70.0,
  "count": 3,
  "cables": [
    {
      "id": "health-003",
      "link_id": "link-003",
      "health_score": 65.5,
      "status": "FAIR"
    }
  ]
}
```

### Get Single Metric
```http
GET /api/v1/cable-health/{metric_id}
```

### Test Cable Health
```http
POST /api/v1/cable-health/test
```

Run a cable health test on a link.

#### Request Body
```json
{
  "link_id": "link-001",
  "test_type": "full",
  "notes": "Scheduled maintenance test"
}
```

#### Test Types

| Value | Description |
|-------|-------------|
| `quick` | Basic connectivity test |
| `full` | Comprehensive cable analysis |
| `extended` | Extended diagnostics |

#### Example Response
```json
{
  "link_id": "link-001",
  "test_passed": true,
  "status": "EXCELLENT",
  "signal_quality": 98,
  "issues_found": [],
  "recommendations": [
    "✅ Link health is EXCELLENT. No issues detected."
  ],
  "test_duration": 5.2,
  "tested_at": "2025-01-17T11:00:00Z"
}
```

### Get Link Health History
```http
GET /api/v1/cable-health/link/{link_id}/history
```

#### Query Parameters

| Parameter | Type | Default | Max | Description |
|-----------|------|---------|-----|-------------|
| `hours` | integer | 24 | 168 | Hours of history |

#### Example Response
```json
{
  "link_id": "link-001",
  "time_range_hours": 24,
  "count": 48,
  "metrics": [
    {
      "id": "health-latest",
      "health_score": 98.5,
      "status": "EXCELLENT",
      "measured_at": "2025-01-17T10:00:00Z"
    }
  ]
}
```

### Get Latest Health for Link
```http
GET /api/v1/cable-health/link/{link_id}/latest
```

### Create Health Metric
```http
POST /api/v1/cable-health
```

### Delete Health Metric
```http
DELETE /api/v1/cable-health/{metric_id}
```

---

## 📡 Monitoring API

### Get Monitoring Status
```http
GET /api/v1/monitoring/status
```

Get current monitoring service status.

#### Example Response
```json
{
  "is_running": true,
  "check_interval_seconds": 60,
  "monitored_devices": 42,
  "monitored_links": 35,
  "recent_events_1h": 5,
  "timestamp": "2025-01-17T11:00:00Z"
}
```

### Run Monitoring Cycle
```http
POST /api/v1/monitoring/run-cycle
```

Manually trigger a monitoring cycle (runs in background).

#### Example Response
```json
{
  "message": "Monitoring cycle started in background",
  "status": "running"
}
```

### Check All Devices
```http
POST /api/v1/monitoring/devices/check-all
```

Check status of all monitored devices.

#### Example Response
```json
{
  "total_devices": 42,
  "checked": 42,
  "up": 38,
  "down": 2,
  "unreachable": 2,
  "errors": 0,
  "timestamp": "2025-01-17T11:00:00Z"
}
```

### Check All Links
```http
POST /api/v1/monitoring/links/check-all
```

Check health of all links.

#### Example Response
```json
{
  "total_links": 35,
  "checked": 35,
  "up": 32,
  "degraded": 2,
  "down": 1,
  "errors": 0,
  "timestamp": "2025-01-17T11:00:00Z"
}
```

### Get Health Summary
```http
GET /api/v1/monitoring/health-summary
```

Get overall network health summary.

#### Example Response
```json
{
  "devices": {
    "total": 42,
    "up": 38,
    "down": 4
  },
  "links": {
    "total": 35,
    "up": 32,
    "degraded": 2,
    "down": 1
  },
  "alerts": {
    "critical_unacknowledged": 3
  },
  "timestamp": "2025-01-17T11:00:00Z"
}
```

---

## 🔍 Discovery API

### Scan Network
```http
POST /api/v1/discovery/scan
```

Scan network for devices.

#### Query Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `network_range` | string | 192.168.1.0/24 | Network range (CIDR) |
| `save_results` | boolean | true | Save to database |

#### Example Request
```bash
curl -X POST "http://localhost:8000/api/v1/discovery/scan?network_range=192.168.1.0/24&save_results=true" \
  -H "Authorization: Bearer <token>"
```

#### Example Response
```json
{
  "network_range": "192.168.1.0/24",
  "devices_found": 10,
  "devices": [
    {
      "ip": "192.168.1.1",
      "mac": "00:1A:2B:3C:4D:01",
      "device_type": "ROUTER",
      "status": "UP",
      "latency_ms": 2.5,
      "method": "ARP"
    }
  ],
  "save_result": {
    "new_devices": 2,
    "updated_devices": 8
  }
}
```

### Scan Network (Background)
```http
POST /api/v1/discovery/scan-background
```

Run network scan in background.

#### Example Response
```json
{
  "message": "Network scan started in background",
  "network_range": "192.168.1.0/24",
  "status": "running"
}
```

### Scan Single Device
```http
POST /api/v1/discovery/scan-device/{ip}
```

#### Query Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `save_result` | boolean | true | Save to database |

### ARP Scan
```http
GET /api/v1/discovery/arp-scan
```

Perform ARP scan on network range.

#### Query Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `network_range` | string | 192.168.1.0/24 | Network range |

#### Example Response
```json
{
  "network_range": "192.168.1.0/24",
  "method": "ARP",
  "devices_found": 10,
  "devices": [
    {
      "ip": "192.168.1.1",
      "mac": "00:1A:2B:3C:4D:01",
      "response_time_ms": 1.2
    }
  ]
}
```

### Ping Sweep
```http
POST /api/v1/discovery/ping-sweep
```

Ping multiple IP addresses.

#### Request Body
```json
{
  "ips": [
    "192.168.1.1",
    "192.168.1.2",
    "192.168.1.3"
  ]
}
```

#### Example Response
```json
{
  "total_ips": 3,
  "alive": 3,
  "dead": 0,
  "results": [
    {
      "ip": "192.168.1.1",
      "is_alive": true,
      "latency_ms": 2.5
    }
  ]
}
```

---

## 🌐 SNMP API

### Get Device SNMP Info
```http
GET /api/v1/snmp/device/{device_id}/info
```

Get SNMP system information from a device.

#### Query Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `community` | string | SNMP community (optional) |

#### Example Response
```json
{
  "host": "192.168.1.1",
  "sysDescr": "Cisco IOS Software...",
  "sysName": "core-router-01",
  "sysLocation": "Server Room A",
  "sysContact": "admin@example.com",
  "sysUpTime": "42 days, 3:15:22",
  "device_type": "ROUTER"
}
```

### Get Device Interfaces
```http
GET /api/v1/snmp/device/{device_id}/interfaces
```

Get SNMP interface information.

#### Example Response
```json
{
  "device_id": "dev-001",
  "device_ip": "192.168.1.1",
  "interface_count": 24,
  "interfaces": [
    {
      "ifIndex": "1",
      "ifDescr": "GigabitEthernet0/0",
      "ifSpeed": 1000000000,
      "ifAdminStatus": "UP",
      "ifOperStatus": "UP",
      "ifInOctets": 1234567890,
      "ifOutOctets": 9876543210
    }
  ]
}
```

### Query OID
```http
POST /api/v1/snmp/query-oid
```

Query a specific OID from a device.

#### Request Body
```json
{
  "ip": "192.168.1.1",
  "oid": "1.3.6.1.2.1.1.1.0",
  "community": "public"
}
```

#### Example Response
```json
{
  "ip": "192.168.1.1",
  "oid": "1.3.6.1.2.1.1.1.0",
  "value": "Cisco IOS Software..."
}
```

### Walk OID
```http
POST /api/v1/snmp/walk-oid
```

Walk an OID tree from a device.

#### Request Body
```json
{
  "ip": "192.168.1.1",
  "base_oid": "1.3.6.1.2.1.2.2",
  "community": "public",
  "max_rows": 100
}
```

### Discover Devices via SNMP
```http
POST /api/v1/snmp/discover-devices
```

Discover multiple devices via SNMP.

#### Request Body
```json
{
  "ips": ["192.168.1.1", "192.168.1.2"],
  "community": "public"
}
```

---

## 📊 Statistics API

### Get Overview
```http
GET /api/v1/statistics/overview
```

Get overall network statistics.

#### Example Response
```json
{
  "devices": {
    "total": 42,
    "up": 38,
    "down": 4,
    "monitored": 40,
    "by_type": {
      "ROUTER": 5,
      "SWITCH": 15,
      "SERVER": 8,
      "PC": 10,
      "AP": 4
    }
  },
  "links": {
    "total": 35,
    "up": 32,
    "degraded": 2
  },
  "ports": {
    "total": 248,
    "up": 210
  },
  "events": {
    "last_24h": 156,
    "critical_24h": 3
  }
}
```

### Get Devices by Type
```http
GET /api/v1/statistics/devices/by-type
```

### Get Devices by Status
```http
GET /api/v1/statistics/devices/by-status
```

### Get Events Timeline
```http
GET /api/v1/statistics/events/timeline
```

#### Query Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `hours` | integer | 24 | Hours to analyze |

### Get Network Health Score
```http
GET /api/v1/statistics/network-health-score
```

Calculate overall network health score.

#### Example Response
```json
{
  "overall_score": 87.5,
  "status": "GOOD",
  "components": {
    "device_health": 90.5,
    "link_health": 91.4,
    "event_impact": 80.0
  },
  "metrics": {
    "devices_up": 38,
    "total_devices": 42,
    "links_up": 32,
    "total_links": 35,
    "critical_events_1h": 1
  }
}
```

#### Health Status Ranges

| Score | Status | Color |
|-------|--------|-------|
| 90-100 | EXCELLENT | 🟢 Green |
| 75-89 | GOOD | 🟢 Green |
| 60-74 | FAIR | 🟡 Yellow |
| 40-59 | POOR | 🟠 Orange |
| 0-39 | CRITICAL | 🔴 Red |

### Get Traffic Summary
```http
GET /api/v1/statistics/traffic-summary
```

Get network traffic summary.

#### Example Response
```json
{
  "total_rx_bytes": 12345678900,
  "total_tx_bytes": 98765432100,
  "total_rx_packets": 1234567,
  "total_tx_packets": 9876543,
  "total_rx_errors": 123,
  "total_tx_errors": 45,
  "total_traffic_bytes": 111111111000
}
```

---

## ✅ Validation API

### Validate IP Address
```http
POST /api/v1/validation/ip
```

#### Request Body
```json
{
  "ip": "192.168.1.1"
}
```

#### Example Response
```json
{
  "value": "192.168.1.1",
  "valid": true,
  "error": null
}
```

### Validate MAC Address
```http
POST /api/v1/validation/mac
```

#### Request Body
```json
{
  "mac": "00:1A:2B:3C:4D:01"
}
```

#### Example Response
```json
{
  "value": "00:1A:2B:3C:4D:01",
  "valid": true,
  "error": null,
  "normalized": "00:1A:2B:3C:4D:01"
}
```

### Validate IP Range
```http
POST /api/v1/validation/ip-range
```

#### Request Body
```json
{
  "ip_range": "192.168.1.0/24"
}
```

### Validate Hostname
```http
POST /api/v1/validation/hostname
```

#### Request Body
```json
{
  "hostname": "core-router-01"
}
```

### Validate Device Data
```http
POST /api/v1/validation/device
```

Validate complete device data.

#### Request Body
```json
{
  "name": "New Device",
  "ip": "192.168.1.10",
  "mac": "00:1A:2B:3C:4D:10",
  "hostname": "device-01",
  "vlan_id": 10
}
```

#### Example Response
```json
{
  "valid": true,
  "errors": null
}
```

Or with errors:
```json
{
  "valid": false,
  "errors": {
    "ip": ["Invalid IP address format"],
    "vlan_id": ["VLAN ID must be between 1 and 4094"]
  }
}
```

### Check IP in Subnet
```http
GET /api/v1/validation/check-ip-in-subnet
```

#### Query Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `ip` | string | IP address |
| `subnet` | string | Subnet in CIDR notation |

#### Example
```http
GET /api/v1/validation/check-ip-in-subnet?ip=192.168.1.50&subnet=192.168.1.0/24
```

#### Example Response
```json
{
  "ip": "192.168.1.50",
  "subnet": "192.168.1.0/24",
  "in_subnet": true
}
```

---

## ❌ Error Handling

### Error Response Format

All errors follow this format:
```json
{
  "detail": "Error message describing what went wrong",
  "status_code": 404
}
```

### Common Error Codes

#### 400 Bad Request
```json
{
  "detail": "Invalid request parameters",
  "status_code": 400
}
```

#### 401 Unauthorized
```json
{
  "detail": "Could not validate credentials",
  "status_code": 401
}
```

#### 403 Forbidden
```json
{
  "detail": "Admin privileges required",
  "status_code": 403
}
```

#### 404 Not Found
```json
{
  "detail": "Device with identifier 'dev-999' not found",
  "status_code": 404
}
```

#### 409 Conflict
```json
{
  "detail": "Device with IP 192.168.1.1 already exists",
  "status_code": 409
}
```

#### 422 Validation Error
```json
{
  "detail": [
    {
      "loc": ["body", "ip"],
      "msg": "Invalid IP address format",
      "type": "value_error"
    }
  ]
}
```

#### 429 Too Many Requests
```json
{
  "detail": "Rate limit exceeded. Max 60 requests per minute.",
  "status_code": 429
}
```

#### 500 Internal Server Error
```json
{
  "detail": "Internal server error",
  "status_code": 500
}
```

---

## ⏱️ Rate Limiting

### Default Limits

| Endpoint Type | Limit |
|--------------|-------|
| Standard | 60 requests/minute |
| Strict | 10 requests/minute |

### Rate Limit Headers

Responses include rate limit information:
```http
X-RateLimit-Limit: 60
X-RateLimit-Remaining: 45
X-RateLimit-Reset: 1705484400
```

### Rate Limit Exceeded Response
```http
HTTP/1.1 429 Too Many Requests
Retry-After: 30

{
  "detail": "Rate limit exceeded. Max 60 requests per 60 seconds."
}
```

---

## 📝 Request Examples

### Using cURL
```bash
# List devices
curl -X GET "http://localhost:8000/api/v1/devices" \
  -H "Authorization: Bearer <token>"

# Create device
curl -X POST "http://localhost:8000/api/v1/devices" \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "New Router",
    "device_type": "ROUTER",
    "ip": "192.168.1.100"
  }'

# Update device
curl -X PUT "http://localhost:8000/api/v1/devices/dev-001" \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"name": "Updated Name"}'

# Delete device
curl -X DELETE "http://localhost:8000/api/v1/devices/dev-001" \
  -H "Authorization: Bearer <token>"
```

### Using Python
```python
import requests

BASE_URL = "http://localhost:8000/api/v1"
TOKEN = "your-jwt-token"

headers = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json"
}

# List devices
response = requests.get(f"{BASE_URL}/devices", headers=headers)
devices = response.json()

# Create device
new_device = {
    "name": "New Router",
    "device_type": "ROUTER",
    "ip": "192.168.1.100"
}
response = requests.post(f"{BASE_URL}/devices", headers=headers, json=new_device)
created = response.json()

# Update device
update_data = {"name": "Updated Name"}
response = requests.put(f"{BASE_URL}/devices/dev-001", headers=headers, json=update_data)

# Delete device
response = requests.delete(f"{BASE_URL}/devices/dev-001", headers=headers)
```

### Using JavaScript (Fetch)
```javascript
const BASE_URL = 'http://localhost:8000/api/v1';
const TOKEN = 'your-jwt-token';

const headers = {
  'Authorization': `Bearer ${TOKEN}`,
  'Content-Type': 'application/json'
};

// List devices
fetch(`${BASE_URL}/devices`, { headers })
  .then(res => res.json())
  .then(devices => console.log(devices));

// Create device
fetch(`${BASE_URL}/devices`, {
  method: 'POST',
  headers,
  body: JSON.stringify({
    name: 'New Router',
    device_type: 'ROUTER',
    ip: '192.168.1.100'
  })
})
  .then(res => res.json())
  .then(device => console.log(device));
```

---

## 🔗 Webhooks (Future Feature)

Webhook support for real-time event notifications is planned for future releases.

---

## 📚 Additional Resources

- **Interactive API Docs:** `/api/docs`
- **API Schema:** `/api/openapi.json`
- **Architecture Guide:** See `ARCHITECTURE.md`
- **Troubleshooting:** See `TROUBLESHOOTING.md`

---

## 📞 Support

For API support:
- Check `/api/docs` for interactive testing
- Review `TROUBLESHOOTING.md` for common issues
- Contact: support@yourdomain.com

---

**API Version:** 1.0  
**Last Updated:** January 17, 2025  
**Base URL:** `/api/v1`