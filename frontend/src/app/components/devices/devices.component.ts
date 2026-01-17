import { Component, OnInit, OnDestroy } from '@angular/core';
import { Router } from '@angular/router';
import { Subject } from 'rxjs';
import { takeUntil, debounceTime, distinctUntilChanged } from 'rxjs/operators';
import { 
  ApiService, 
  Device, 
  DeviceCreate, 
  DeviceStatus, 
  DeviceType 
} from '../../services/api.service';
import { 
  WebsocketService, 
  DeviceStatusUpdate 
} from '../../services/websocket.service';
import { NotificationService } from '../../services/notification.service';

@Component({
  selector: 'app-devices',
  templateUrl: './devices.component.html',
  styleUrls: ['./devices.component.scss']
})
export class DevicesComponent implements OnInit, OnDestroy {
  private destroy$ = new Subject<void>();
  private searchSubject$ = new Subject<string>();
  
  devices: Device[] = [];
  filteredDevices: Device[] = [];
  
  searchTerm = '';
  selectedStatus: DeviceStatus | '' = '';
  selectedType: DeviceType | '' = '';
  
  currentPage = 1;
  pageSize = 20;
  totalDevices = 0;
  totalPages = 0;
  pages: number[] = [];
  
  isLoading = false;
  showAddModal = false;
  
  newDevice: DeviceCreate = {
    name: '',
    device_type: 'router',
    is_monitored: true
  };
  
  deviceStatuses: DeviceStatus[] = ['UP', 'DOWN', 'UNKNOWN'];
  deviceTypes: DeviceType[] = ['router', 'switch', 'pc', 'server', 'printer', 'access_point'];

  constructor(
    private api: ApiService,
    private ws: WebsocketService,
    private notifications: NotificationService,
    private router: Router
  ) {}

  ngOnInit(): void {
    this.loadDevices();
    this.setupSearch();
    this.subscribeToUpdates();
  }

  ngOnDestroy(): void {
    this.destroy$.next();
    this.destroy$.complete();
  }

  // ==================== DATA LOADING ====================

  loadDevices(): void {
    this.isLoading = true;
    
    const params: any = {
      page: this.currentPage,
      page_size: this.pageSize
    };
    
    if (this.selectedStatus) {
      params.status = this.selectedStatus;
    }
    
    if (this.selectedType) {
      params.device_type = this.selectedType;
    }
    
    this.api.getDevices(params).subscribe({
      next: (devices) => {
        this.devices = devices;
        this.applyClientSideFilter();
        this.isLoading = false;
      },
      error: (error) => {
        this.notifications.showApiError(error);
        this.isLoading = false;
      }
    });
  }

  private setupSearch(): void {
    this.searchSubject$
      .pipe(
        debounceTime(300),
        distinctUntilChanged(),
        takeUntil(this.destroy$)
      )
      .subscribe(() => {
        this.applyClientSideFilter();
      });
  }

  private subscribeToUpdates(): void {
    this.ws.getDeviceStatusUpdates()
      .pipe(takeUntil(this.destroy$))
      .subscribe((update: DeviceStatusUpdate) => {
        const device = this.devices.find(d => d.id === update.device_id);
        if (device) {
          device.status = update.status;
          this.applyClientSideFilter();
        }
      });
  }

  // ==================== FILTERING ====================

  private applyClientSideFilter(): void {
    let filtered = [...this.devices];
    
    // Apply search filter
    if (this.searchTerm) {
      const term = this.searchTerm.toLowerCase();
      filtered = filtered.filter(device => 
        device.name.toLowerCase().includes(term) ||
        (device.ip && device.ip.toLowerCase().includes(term)) ||
        (device.mac && device.mac.toLowerCase().includes(term)) ||
        (device.hostname && device.hostname.toLowerCase().includes(term))
      );
    }
    
    this.filteredDevices = filtered;
    this.totalDevices = this.filteredDevices.length;
    this.calculatePagination();
  }

  onSearchChange(value: string): void {
    this.searchSubject$.next(value);
  }

  onFilterChange(): void {
    this.currentPage = 1;
    this.loadDevices();
  }

  clearFilters(): void {
    this.searchTerm = '';
    this.selectedStatus = '';
    this.selectedType = '';
    this.currentPage = 1;
    this.loadDevices();
  }

  // ==================== PAGINATION ====================

  private calculatePagination(): void {
    this.totalPages = Math.ceil(this.totalDevices / this.pageSize);
    this.pages = Array.from({ length: this.totalPages }, (_, i) => i + 1);
  }

  get visiblePages(): number[] {
    const start = Math.max(0, this.currentPage - 3);
    const end = Math.min(this.totalPages, this.currentPage + 2);
    return this.pages.slice(start, end);
  }

  previousPage(): void {
    if (this.currentPage > 1) {
      this.currentPage--;
      this.loadDevices();
    }
  }

  nextPage(): void {
    if (this.currentPage < this.totalPages) {
      this.currentPage++;
      this.loadDevices();
    }
  }

  goToPage(page: number): void {
    this.currentPage = page;
    this.loadDevices();
  }

  // ==================== MODAL ====================

  openAddModal(): void {
    this.showAddModal = true;
    this.resetNewDeviceForm();
  }

  closeAddModal(): void {
    this.showAddModal = false;
    this.resetNewDeviceForm();
  }

  private resetNewDeviceForm(): void {
    this.newDevice = {
      name: '',
      device_type: 'router',
      is_monitored: true
    };
  }

  // ==================== CRUD OPERATIONS ====================

  createDevice(): void {
    if (!this.newDevice.name) {
      this.notifications.warning('Please enter a device name');
      return;
    }
    
    this.api.createDevice(this.newDevice).subscribe({
      next: (device) => {
        this.notifications.success(`Device "${device.name}" created successfully`);
        this.closeAddModal();
        this.loadDevices();
      },
      error: (error) => {
        this.notifications.showApiError(error);
      }
    });
  }

  deleteDevice(device: Device): void {
    if (!confirm(`Are you sure you want to delete "${device.name}"?`)) {
      return;
    }
    
    this.api.deleteDevice(device.id).subscribe({
      next: () => {
        this.notifications.success(`Device "${device.name}" deleted`);
        this.loadDevices();
      },
      error: (error) => {
        this.notifications.showApiError(error);
      }
    });
  }

  // ==================== DEVICE ACTIONS ====================

  viewDevice(device: Device): void {
    this.router.navigate(['/devices', device.id]);
  }

  pingDevice(device: Device): void {
    this.notifications.info(`Pinging ${device.name}...`);
    
    this.api.pingDevice(device.id).subscribe({
      next: (result) => {
        if (result.is_alive) {
          this.notifications.success(
            `${device.name} is UP (${result.response_time_ms}ms)`
          );
        } else {
          this.notifications.error(`${device.name} is DOWN`);
        }
      },
      error: (error) => {
        this.notifications.showApiError(error);
      }
    });
  }

  exportDevices(): void {
    const csv = this.devicesToCSV(this.filteredDevices);
    this.downloadCSV(csv, `devices-${Date.now()}.csv`);
    this.notifications.success('Devices exported to CSV');
  }

  private devicesToCSV(devices: Device[]): string {
    const headers = ['Name', 'Type', 'Status', 'IP', 'MAC', 'Location', 'Last Seen'];
    const rows = devices.map(d => [
      d.name,
      d.device_type,
      d.status,
      d.ip || '',
      d.mac || '',
      d.location || '',
      d.last_seen || ''
    ]);
    
    return [headers, ...rows].map(row => row.join(',')).join('\n');
  }

  private downloadCSV(csv: string, filename: string): void {
    const blob = new Blob([csv], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    window.URL.revokeObjectURL(url);
  }

  // ==================== UTILITIES ====================

  getStatusClass(status: DeviceStatus): string {
    return `status-${status.toLowerCase()}`;
  }

  getTypeIcon(type: DeviceType): string {
    const icons: Record<DeviceType, string> = {
      router: '🔷',
      switch: '🔹',
      pc: '💻',
      server: '🖥️',
      printer: '🖨️',
      access_point: '📡'
    };
    return icons[type] || '📦';
  }
}