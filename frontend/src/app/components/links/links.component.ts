import { Component, OnInit, OnDestroy } from '@angular/core';
import { Router } from '@angular/router';
import { Subject } from 'rxjs';
import { takeUntil } from 'rxjs/operators';
import {
  ApiService,
  Link,
  LinkCreate,
  LinkStatus,
  Device
} from '../../services/api.service';
import { WebsocketService, LinkStatusUpdate } from '../../services/websocket.service';
import { NotificationService } from '../../services/notification.service';

@Component({
  selector: 'app-links',
  templateUrl: './links.component.html',
  styleUrls: ['./links.component.scss']
})
export class LinksComponent implements OnInit, OnDestroy {
  private destroy$ = new Subject<void>();

  links: Link[] = [];
  devices: Device[] = [];

  selectedStatus: LinkStatus | '' = '';
  currentPage = 1;
  pageSize = 20;
  totalLinks = 0;

  isLoading = false;
  showAddModal = false;

  newLink: LinkCreate = {
    source_device_id: '',
    target_device_id: ''
  };

  linkStatuses: LinkStatus[] = ['UP', 'DOWN', 'DEGRADED', 'UNKNOWN'];

  constructor(
    private api: ApiService,
    private ws: WebsocketService,
    private notifications: NotificationService,
    private router: Router
  ) {}

  ngOnInit(): void {
    this.loadLinks();
    this.loadDevices();
    this.subscribeToUpdates();
  }

  ngOnDestroy(): void {
    this.destroy$.next();
    this.destroy$.complete();
  }

  loadLinks(): void {
    this.isLoading = true;

    const params: any = {
      page: this.currentPage,
      page_size: this.pageSize
    };

    if (this.selectedStatus) {
      params.status = this.selectedStatus;
    }

    this.api.getLinks(params).subscribe({
      next: (links) => {
        this.links = links;
        // if your API returns total count separately, update totalLinks there
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
    this.ws.getLinkStatusUpdates()
      .pipe(takeUntil(this.destroy$))
      .subscribe((update: LinkStatusUpdate) => {
        const link = this.links.find(l => l.id === update.link_id);
        if (link) {
          link.status = update.status;
        }
      });
  }

  onFilterChange(): void {
    this.currentPage = 1;
    this.loadLinks();
  }

  openAddModal(): void {
    this.showAddModal = true;
    this.resetNewLinkForm();
  }

  closeAddModal(): void {
    this.showAddModal = false;
    this.resetNewLinkForm();
  }

  private resetNewLinkForm(): void {
    this.newLink = {
      source_device_id: '',
      target_device_id: '',
      bandwidth_mbps: undefined,
      source_port_id: undefined,
      target_port_id: undefined,
      link_type: undefined,
      description: undefined
      // vlanid is optional and will be filled from the form if you add it to LinkCreate
    };
  }

  createLink(): void {
    if (!this.newLink.source_device_id || !this.newLink.target_device_id) {
      this.notifications.warning('Please select both source and target devices');
      return;
    }

    if (this.newLink.source_device_id === this.newLink.target_device_id) {
      this.notifications.warning('Source and target must be different devices');
      return;
    }

    this.api.createLink(this.newLink).subscribe({
      next: () => {
        this.notifications.success('Link created successfully');
        this.closeAddModal();
        this.loadLinks();
      },
      error: (error) => {
        this.notifications.showApiError(error);
      }
    });
  }

  deleteLink(link: Link): void {
    if (!confirm('Are you sure you want to delete this link?')) {
      return;
    }

    this.api.deleteLink(link.id).subscribe({
      next: () => {
        this.notifications.success('Link deleted');
        this.loadLinks();
      },
      error: (error) => {
        this.notifications.showApiError(error);
      }
    });
  }

  testLink(link: Link): void {
    this.api.testLink(link.id).subscribe({
      next: () => {
        this.notifications.success('Link test completed');
        this.loadLinks();
      },
      error: (error) => {
        this.notifications.showApiError(error);
      }
    });
  }

  viewLink(link: Link): void {
    // Navigate to link detail if you have that component
    this.notifications.info(`Link details: ${link.id}`);
  }

  getStatusClass(status: LinkStatus): string {
    return `status-${status.toLowerCase()}`;
  }

  getDeviceName(deviceId: string): string {
    const device = this.devices.find(d => d.id === deviceId);
    return device ? device.name : deviceId;
  }
}
