import { Component, OnInit, OnDestroy } from '@angular/core';
import { Subject } from 'rxjs';
import { takeUntil } from 'rxjs/operators';
import { ApiService, Port, PortStatus, Device } from '../../services/api.service';
import { WebsocketService, PortStatusUpdate } from '../../services/websocket.service';
import { NotificationService } from '../../services/notification.service';

@Component({
  selector: 'app-ports',
  templateUrl: './ports.component.html',
  styleUrls: ['./ports.component.scss']
})
export class PortsComponent implements OnInit, OnDestroy {
  private destroy$ = new Subject<void>();
  
  ports: Port[] = [];
  devices: Device[] = [];
  
  selectedStatus: PortStatus | '' = '';
  selectedDeviceId = '';
  
  currentPage = 1;
  pageSize = 20;
  totalPorts = 0;
  
  isLoading = false;
  
  portStatuses: PortStatus[] = ['UP', 'DOWN', 'DISABLED'];

  constructor(
    private api: ApiService,
    private ws: WebsocketService,
    private notifications: NotificationService
  ) {}

  ngOnInit(): void {
    this.loadPorts();
    this.loadDevices();
    this.subscribeToUpdates();
  }

  ngOnDestroy(): void {
    this.destroy$.next();
    this.destroy$.complete();
  }

  loadPorts(): void {
    this.isLoading = true;
    
    const params: any = {
      page: this.currentPage,
      page_size: this.pageSize
    };
    
    if (this.selectedStatus) params.status = this.selectedStatus;
    if (this.selectedDeviceId) params.device_id = this.selectedDeviceId;
    
    this.api.getPorts(params).subscribe({
      next: (ports) => {
        this.ports = ports;
        this.isLoading = false;
      },
      error: (error) => {
        this.notifications.showApiError(error);
        this.isLoading = false;
      }
    });
  }

  loadDevices(): void {
    this.api.getDevices({ page_size: 1000 }).subscribe({
      next: (devices) => {
        this.devices = devices;
      },
      error: (error) => {
        console.error('Error loading devices:', error);
      }
    });
  }

  private subscribeToUpdates(): void {
    this.ws.getPortStatusUpdates()
      .pipe(takeUntil(this.destroy$))
      .subscribe((update: PortStatusUpdate) => {
        const port = this.ports.find(p => p.id === update.port_id);
        if (port) {
          port.status = update.status;
        }
      });
  }

  onFilterChange(): void {
    this.currentPage = 1;
    this.loadPorts();
  }

  getStatusClass(status: PortStatus): string {
    return `status-${status.toLowerCase()}`;
  }

  getDeviceName(deviceId: string): string {
    const device = this.devices.find(d => d.id === deviceId);
    return device ? device.name : deviceId;
  }

  formatBytes(bytes: number): string {
    if (bytes === 0) return '0 B';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB', 'TB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
  }
}