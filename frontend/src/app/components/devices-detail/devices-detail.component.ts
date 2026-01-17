import { Component, OnInit, OnDestroy } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { Subject } from 'rxjs';
import { takeUntil } from 'rxjs/operators';
import {
  ApiService,
  Device,
  DeviceUpdate,
  Port,
  Link,
  Event
} from '../../services/api.service';
import {
  WebsocketService,
  DeviceStatusUpdate
} from '../../services/websocket.service';
import { NotificationService } from '../../services/notification.service';

@Component({
  selector: 'app-device-detail',
  templateUrl: './device-detail.component.html',
  styleUrls: ['./device-detail.component.scss']
})
export class DeviceDetailComponent implements OnInit, OnDestroy {
  private destroy = new Subject<void>();

  deviceId!: string;
  device: Device | null = null;
  ports: Port[] = [];
  links: Link[] = [];
  events: Event[] = [];

  // UI State
  isLoading = true;
  isEditing = false;
  activeTab: 'overview' | 'ports' | 'links' | 'events' | 'settings' = 'overview';

  // Edit form (matches DeviceUpdate)
  editForm: DeviceUpdate = {};

  // Ping result
  pingResult: any = null;
  isPinging = false;

  constructor(
    private route: ActivatedRoute,
    private router: Router,
    private api: ApiService,
    private ws: WebsocketService,
    private notifications: NotificationService
  ) {}

  ngOnInit(): void {
    this.deviceId = this.route.snapshot.params['id'];
    this.loadDeviceDetails();
    this.subscribeToUpdates();
  }

  ngOnDestroy(): void {
    this.destroy.next();
    this.destroy.complete();
  }

  /**
   * Map full Device (with nulls, snake_case) to DeviceUpdate (optionals, same snake_case keys).
   */
  private mapDeviceToUpdate(device: Device): DeviceUpdate {
    return {
      name: device.name,
      ip: device.ip ?? undefined,
      mac: device.mac ?? undefined,
      hostname: device.hostname ?? undefined,
      device_type: device.device_type,
      location: device.location ?? undefined,
      description: device.description ?? undefined,
      manufacturer: device.manufacturer ?? undefined,
      model: device.model ?? undefined,
      serial_number: device.serial_number ?? undefined,
      firmware_version: device.firmware_version ?? undefined,
      is_monitored: device.is_monitored,
      snmp_enabled: device.snmp_enabled,
      snmp_community: device.snmp_community ?? undefined,
      vlan_id: device.vlan_id ?? undefined
    };
  }

  // ==================== DATA LOADING ====================

  private loadDeviceDetails(): void {
    this.isLoading = true;

    // Device
    this.api.getDevice(this.deviceId).subscribe({
      next: (device) => {
        this.device = device;
        this.editForm = this.mapDeviceToUpdate(device);
        this.isLoading = false;
      },
      error: (error) => {
        console.error('Error loading device', error);
        this.notifications.showApiError(error);
        this.isLoading = false;
        this.router.navigate(['devices']);
      }
    });

    // Ports
    this.api.getDevicePorts(this.deviceId).subscribe({
      next: (ports) => {
        this.ports = ports;
      },
      error: (error) => {
        console.error('Error loading ports', error);
      }
    });

    // Links
    this.api.getDeviceLinks(this.deviceId).subscribe({
      next: (links) => {
        this.links = links;
      },
      error: (error) => {
        console.error('Error loading links', error);
      }
    });

    // Events
    this.api.getDeviceEvents(this.deviceId, 20).subscribe({
      next: (events) => {
        this.events = events;
      },
      error: (error) => {
        console.error('Error loading events', error);
      }
    });
  }

  // ==================== WEBSOCKET ====================

  private subscribeToUpdates(): void {
    this.ws
      .getDeviceStatusUpdates()
      .pipe(takeUntil(this.destroy))
      .subscribe((update: DeviceStatusUpdate) => {
        if (update.device_id === this.deviceId) {
          if (this.device) {
            this.device.status = update.status as any;
          }
          if (update.response_time_ms != null) {
            this.pingResult = {
              is_alive: update.status === 'UP',
              response_time_ms: update.response_time_ms
            };
          }
        }
      });
  }

  // ==================== TABS ====================

  setActiveTab(tab: typeof this.activeTab): void {
    this.activeTab = tab;
  }

  // ==================== EDIT MODE ====================

  enterEditMode(): void {
    if (this.device) {
      this.editForm = this.mapDeviceToUpdate(this.device);
      this.isEditing = true;
    }
  }

  cancelEdit(): void {
    this.isEditing = false;
    if (this.device) {
      this.editForm = this.mapDeviceToUpdate(this.device);
    }
  }

  saveChanges(): void {
    if (!this.device) return;

    this.api.updateDevice(this.deviceId, this.editForm).subscribe({
      next: (updatedDevice) => {
        this.device = updatedDevice;
        this.editForm = this.mapDeviceToUpdate(updatedDevice);
        this.isEditing = false;
        this.notifications.success('Device updated successfully');
      },
      error: (error) => {
        this.notifications.showApiError(error);
      }
    });
  }

  // ==================== ACTIONS ====================

  pingDevice(): void {
    this.isPinging = true;
    this.pingResult = null;

    this.api.pingDevice(this.deviceId).subscribe({
      next: (result) => {
        this.pingResult = result;
        this.isPinging = false;

        const isAlive = result.is_alive;
        const rt = result.response_time_ms;
        const message = isAlive
          ? `Device is UP (${rt}ms)`
          : 'Device is DOWN';

        if (isAlive) {
          this.notifications.success(message);
        } else {
          this.notifications.error(message);
        }
      },
      error: (error) => {
        this.isPinging = false;
        this.notifications.showApiError(error);
      }
    });
  }

  deleteDevice(): void {
    if (!this.device) return;

    const confirmed = confirm(
      `Are you sure you want to delete ${this.device.name}? This action cannot be undone.`
    );
    if (!confirmed) return;

    this.api.deleteDevice(this.deviceId).subscribe({
      next: () => {
        this.notifications.success(`Device ${this.device?.name} deleted`);
        this.router.navigate(['devices']);
      },
      error: (error) => {
        this.notifications.showApiError(error);
      }
    });
  }

  refreshData(): void {
    this.loadDeviceDetails();
    this.notifications.info('Refreshing device data...');
  }

  viewPort(port: Port): void {
    // if you implement port-detail route later
    this.router.navigate(['ports', port.id]);
    this.notifications.info(`Port ${port.port_name} details`);
  }

  viewLink(link: Link): void {
    this.router.navigate(['links', link.id]);
  }

  acknowledgeEvent(event: Event): void {
    this.api.acknowledgeEvent(event.id, 'device-detail-user').subscribe({
      next: () => {
        event.acknowledged = true;
        this.notifications.success('Event acknowledged');
      },
      error: (error) => {
        this.notifications.showApiError(error);
      }
    });
  }

  // ==================== COMPUTED PROPERTIES ====================

  get statusClass(): string {
    if (!this.device) return '';
    return `status-${this.device.status.toLowerCase()}`;
  }

  get deviceTypeIcon(): string {
    if (!this.device) return '';
    const icons: Record<Device['device_type'], string> = {
      router: 'router',
      switch: 'switch',
      pc: 'pc',
      server: 'server',
      printer: 'printer',
      access_point: 'accesspoint'
    };
    return icons[this.device.device_type] || 'device';
  }

  get activePorts(): Port[] {
    return this.ports.filter((p) => p.status === 'UP');
  }

  get inactivePorts(): Port[] {
    return this.ports.filter((p) => p.status !== 'UP');
  }

  get activeLinks(): Link[] {
    return this.links.filter((l) => l.status === 'UP');
  }

  get criticalEvents(): Event[] {
    return this.events.filter(
      (e) => e.severity === 'CRITICAL' && !e.acknowledged
    );
  }

  formatTimestamp(timestamp: string): string {
    const date = new Date(timestamp);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffMins = Math.floor(diffMs / 60000);

    if (diffMins < 1) return 'Just now';
    if (diffMins < 60) return `${diffMins}m ago`;
    const diffHours = Math.floor(diffMins / 60);
    if (diffHours < 24) return `${diffHours}h ago`;
    const diffDays = Math.floor(diffHours / 24);
    return `${diffDays}d ago`;
  }

  getPortStatusClass(status: string): string {
    return `port-status-${status.toLowerCase()}`;
  }

  getLinkStatusClass(status: string): string {
    return `link-status-${status.toLowerCase()}`;
  }

  getEventSeverityClass(severity: string): string {
    return `severity-${severity.toLowerCase()}`;
  }
}
