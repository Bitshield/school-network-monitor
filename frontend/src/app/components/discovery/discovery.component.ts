import { Component, OnInit } from '@angular/core';
import { ApiService } from '../../services/api.service';
import { NotificationService } from '../../services/notification.service';

interface ScanResult {
  ip: string;
  mac: string | null;
  hostname: string | null;
  manufacturer: string | null;
  is_alive: boolean;
  response_time_ms: number | null;
}

@Component({
  selector: 'app-discovery',
  templateUrl: './discovery.component.html',
  styleUrls: ['./discovery.component.scss']
})
export class DiscoveryComponent implements OnInit {
  networkRange = '192.168.1.0/24';
  saveResults = true;
  
  isScanning = false;
  scanProgress = 0;
  
  discoveredDevices: ScanResult[] = [];
  totalFound = 0;
  aliveCount = 0;
  
  selectedDevices: string[] = [];
  
  activeScanType: 'network' | 'arp' | 'single' = 'network';
  singleDeviceIP = '';

  constructor(
    private api: ApiService,
    private notifications: NotificationService
  ) {}

  ngOnInit(): void {}

  startNetworkScan(): void {
    if (!this.networkRange) {
      this.notifications.warning('Please enter a network range');
      return;
    }
    
    this.isScanning = true;
    this.scanProgress = 0;
    this.discoveredDevices = [];
    
    this.api.scanNetwork(this.networkRange, this.saveResults).subscribe({
      next: (result) => {
        this.discoveredDevices = result.devices;
        this.totalFound = result.devices_found;
        this.aliveCount = result.devices.filter((d: ScanResult) => d.is_alive).length;
        this.isScanning = false;
        this.scanProgress = 100;
        this.notifications.success(`Found ${this.totalFound} devices`);
      },
      error: (error) => {
        this.isScanning = false;
        this.scanProgress = 0;
        this.notifications.showApiError(error);
      }
    });
    
    this.simulateProgress();
  }

  startARPScan(): void {
    if (!this.networkRange) {
      this.notifications.warning('Please enter a network range');
      return;
    }
    
    this.isScanning = true;
    this.scanProgress = 0;
    this.discoveredDevices = [];
    
    this.api.arpScan(this.networkRange).subscribe({
      next: (result) => {
        this.discoveredDevices = result.devices;
        this.totalFound = result.devices_found;
        this.aliveCount = result.devices.length;
        this.isScanning = false;
        this.scanProgress = 100;
        this.notifications.success(`Found ${this.totalFound} devices`);
      },
      error: (error) => {
        this.isScanning = false;
        this.notifications.showApiError(error);
      }
    });
    
    this.simulateProgress();
  }

  scanSingleDevice(): void {
    if (!this.singleDeviceIP) {
      this.notifications.warning('Please enter an IP address');
      return;
    }
    
    this.isScanning = true;
    this.discoveredDevices = [];
    
    this.api.scanSingleDevice(this.singleDeviceIP, this.saveResults).subscribe({
      next: (result) => {
        if (result.found && result.device) {
          this.discoveredDevices = [result.device];
          this.totalFound = 1;
          this.aliveCount = result.device.is_alive ? 1 : 0;
          this.notifications.success('Device found');
        } else {
          this.notifications.warning('Device not reachable');
        }
        this.isScanning = false;
      },
      error: (error) => {
        this.isScanning = false;
        this.notifications.showApiError(error);
      }
    });
  }

  private simulateProgress(): void {
    const interval = setInterval(() => {
      if (this.scanProgress < 90) {
        this.scanProgress += Math.random() * 10;
      }
      if (!this.isScanning || this.scanProgress >= 100) {
        clearInterval(interval);
      }
    }, 500);
  }

  toggleDeviceSelection(ip: string): void {
    const index = this.selectedDevices.indexOf(ip);
    if (index > -1) {
      this.selectedDevices.splice(index, 1);
    } else {
      this.selectedDevices.push(ip);
    }
  }

  selectAll(): void {
    this.selectedDevices = this.discoveredDevices.map(d => d.ip);
  }

  deselectAll(): void {
    this.selectedDevices = [];
  }

  addSelectedToMonitoring(): void {
    if (this.selectedDevices.length === 0) {
      this.notifications.warning('No devices selected');
      return;
    }
    
    let successCount = 0;
    
    this.selectedDevices.forEach((ip) => {
      const device = this.discoveredDevices.find(d => d.ip === ip);
      if (!device) return;
      
      const deviceData = {
        name: device.hostname || `Device-${ip.split('.').pop()}`,
        ip: device.ip,
        mac: device.mac || undefined,
        hostname: device.hostname || undefined,
        device_type: 'pc' as const,
        is_monitored: true
      };
      
      this.api.createDevice(deviceData).subscribe({
        next: () => {
          successCount++;
          if (successCount === this.selectedDevices.length) {
            this.notifications.success(`Added ${successCount} devices`);
            this.selectedDevices = [];
          }
        }
      });
    });
  }

  exportResults(): void {
    if (this.discoveredDevices.length === 0) {
      this.notifications.warning('No results to export');
      return;
    }
    
    const csv = this.devicesToCSV(this.discoveredDevices);
    this.downloadCSV(csv, `discovery-${Date.now()}.csv`);
    this.notifications.success('Results exported');
  }

  private devicesToCSV(devices: ScanResult[]): string {
    const headers = ['IP', 'MAC', 'Hostname', 'Manufacturer', 'Status', 'Response Time'];
    const rows = devices.map(d => [
      d.ip,
      d.mac || '',
      d.hostname || '',
      d.manufacturer || '',
      d.is_alive ? 'Alive' : 'Down',
      d.response_time_ms?.toString() || ''
    ]);
    
    return [headers, ...rows].map(row => row.join(',')).join('\n');
  }

  private downloadCSV(csv: string, filename: string): void {
    const blob = new Blob([csv], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    a.click();
    window.URL.revokeObjectURL(url);
  }

  getStatusClass(isAlive: boolean): string {
    return isAlive ? 'status-alive' : 'status-down';
  }
}