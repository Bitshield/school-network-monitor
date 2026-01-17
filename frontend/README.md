# School Network Monitor - Angular Frontend (Part 1: Services & Configuration)

## Overview
This is Part 1 of the complete Angular frontend for the School Network Monitor application. This part includes all core services and configuration files that match your backend API endpoints.

## What's Included

### Services (`src/app/services/`)

1. **api.service.ts** - Complete API service with ALL backend endpoints:
   - Devices (CRUD, ping, ports, links, events)
   - Ports (CRUD, statistics)
   - Links (CRUD, test, health history)
   - Events (CRUD, acknowledge, resolve, bulk operations)
   - Cable Health (metrics, testing, history)
   - Monitoring (status, cycles, health summary)
   - Discovery (network scan, ARP scan, ping sweep)
   - SNMP (device info, interfaces, OID query/walk)
   - Statistics (overview, charts, health score, traffic)
   - Validation (IP, MAC, hostname, device data)

2. **websocket.service.ts** - Real-time WebSocket service:
   - Auto-reconnection with exponential backoff
   - Heartbeat/ping mechanism
   - Message type filtering
   - Topology, device, link, port, event updates
   - Connection status tracking

3. **notification.service.ts** - Toast notification system:
   - Success, error, warning, info notifications
   - Custom notifications with actions
   - API error handling

4. **error.interceptor.ts** - HTTP error interceptor:
   - Centralized error handling
   - Automatic error notifications
   - Error logging

### Configuration Files

5. **environment.ts** - Development environment:
   - API and WebSocket URLs
   - Feature flags
   - Monitoring, WebSocket, UI settings
   - Discovery and SNMP configuration
   - Chart colors

6. **environment.prod.ts** - Production environment

### Module Files

7. **app.module.ts** - Main application module
8. **app-routing.module.ts** - Routing configuration

## File Structure
```
src/
├── app/
│   ├── services/
│   │   ├── api.service.ts
│   │   ├── websocket.service.ts
│   │   ├── notification.service.ts
│   │   └── error.interceptor.ts
│   ├── app.module.ts
│   └── app-routing.module.ts
└── environments/
    ├── environment.ts
    └── environment.prod.ts
```

## Installation

1. Copy files to your Angular project:
   ```bash
   # Services
   cp api.service.ts src/app/services/
   cp websocket.service.ts src/app/services/
   cp notification.service.ts src/app/services/
   cp error.interceptor.ts src/app/services/
   
   # Configuration
   cp environment.ts src/environments/
   cp environment.prod.ts src/environments/
   
   # Modules
   cp app.module.ts src/app/
   cp app-routing.module.ts src/app/
   ```

2. Install required dependencies:
   ```bash
   npm install rxjs
   ```

## API Service Usage Examples

### Devices
```typescript
// Get all devices
this.api.getDevices({ page: 1, page_size: 20, status: 'UP' })
  .subscribe(devices => console.log(devices));

// Create device
this.api.createDevice({
  name: 'Router-1',
  ip: '192.168.1.1',
  device_type: 'router',
  is_monitored: true
}).subscribe(device => console.log('Created:', device));

// Ping device
this.api.pingDevice('device-id')
  .subscribe(result => console.log('Ping result:', result));
```

### Events
```typescript
// Get critical events
this.api.getCriticalEvents(24)
  .subscribe(events => console.log(events));

// Acknowledge event
this.api.acknowledgeEvent('event-id', 'admin', 'Investigating')
  .subscribe(() => console.log('Acknowledged'));
```

### Discovery
```typescript
// Scan network
this.api.scanNetwork('192.168.1.0/24', true)
  .subscribe(result => console.log('Found:', result.devices_found));

// ARP scan
this.api.arpScan('192.168.1.0/24')
  .subscribe(result => console.log('Devices:', result.devices));
```

### Statistics
```typescript
// Get network health score
this.api.getNetworkHealthScore()
  .subscribe(health => console.log('Score:', health.overall_score));

// Get statistics overview
this.api.getStatisticsOverview()
  .subscribe(stats => console.log(stats));
```

## WebSocket Service Usage

```typescript
import { WebsocketService } from './services/websocket.service';

constructor(private ws: WebsocketService) {
  // Listen for topology updates
  this.ws.getTopologyUpdates().subscribe(topology => {
    console.log('Topology updated:', topology);
  });

  // Listen for device status changes
  this.ws.getDeviceStatusUpdates().subscribe(status => {
    console.log('Device status:', status);
  });

  // Listen for events
  this.ws.getEventNotifications().subscribe(event => {
    console.log('New event:', event);
  });

  // Check connection status
  this.ws.connectionStatus$.subscribe(status => {
    console.log('WebSocket status:', status);
  });
}

// Request topology update
this.ws.requestTopologyUpdate();

// Subscribe to specific device
this.ws.subscribeToDevice('device-id');
```

## Notification Service Usage

```typescript
import { NotificationService } from './services/notification.service';

constructor(private notifications: NotificationService) {}

// Show notifications
this.notifications.success('Device added successfully');
this.notifications.error('Failed to connect to device');
this.notifications.warning('High latency detected');
this.notifications.info('Scan completed');

// Show API errors
this.api.createDevice(deviceData).subscribe({
  next: (device) => this.notifications.success('Device created'),
  error: (err) => this.notifications.showApiError(err)
});
```

## Environment Configuration

Update `environment.ts` with your backend URLs:

```typescript
export const environment = {
  production: false,
  apiUrl: 'http://localhost:8000/api/v1',  // Your backend API
  wsUrl: 'ws://localhost:8000/ws',          // Your WebSocket endpoint
  // ... other settings
};
```

## Next Steps

Part 2 will include:
- Network Map Component (Cytoscape visualization)
- Dashboard Component
- Device List & Detail Components
- And more...

## API Endpoints Covered

✅ All `/devices` endpoints (11 endpoints)
✅ All `/ports` endpoints (6 endpoints)
✅ All `/links` endpoints (6 endpoints)
✅ All `/events` endpoints (10 endpoints)
✅ All `/cable-health` endpoints (7 endpoints)
✅ All `/monitoring` endpoints (5 endpoints)
✅ All `/discovery` endpoints (5 endpoints)
✅ All `/snmp` endpoints (5 endpoints)
✅ All `/statistics` endpoints (6 endpoints)
✅ All `/validation` endpoints (6 endpoints)

**Total: 67+ API endpoints fully implemented**

## TypeScript Interfaces

All backend models are fully typed with TypeScript interfaces:
- Device, DeviceCreate, DeviceUpdate
- Port, PortCreate, PortUpdate
- Link, LinkCreate, LinkUpdate
- Event, EventCreate
- CableHealthMetrics, CableHealthTestResult
- And many more...

## Notes

- All services use RxJS Observables
- Error handling is centralized through the interceptor
- WebSocket auto-reconnects on connection loss
- Type-safe API calls with full IntelliSense support
- Production-ready with environment configuration

---

**Ready for Part 2?** Next parts will cover all components, starting with the network topology visualization!