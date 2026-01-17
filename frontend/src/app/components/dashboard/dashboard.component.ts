import { Component, OnInit, OnDestroy } from '@angular/core';
import { interval, Subject } from 'rxjs';
import { takeUntil, switchMap, startWith } from 'rxjs/operators';
import { 
  ApiService, 
  Device, 
  Event, 
  StatisticsOverview, 
  NetworkHealthScore 
} from '../../services/api.service';
import { 
  WebsocketService, 
  EventNotification, 
  DeviceStatusUpdate,
  ConnectionStatus 
} from '../../services/websocket.service';
import { NotificationService } from '../../services/notification.service';
import { environment } from '../../../environments/environment';

interface DeviceStatusCount {
  status: string;
  count: number;
  percentage: number;
  color: string;
}

interface EventSummary {
  total: number;
  critical: number;
  warning: number;
  info: number;
  unacknowledged: number;
}

@Component({
  selector: 'app-dashboard',
  templateUrl: './dashboard.component.html',
  styleUrls: ['./dashboard.component.scss']
})
export class DashboardComponent implements OnInit, OnDestroy {
  private destroy$ = new Subject<void>();
  
  // Statistics
  statistics: StatisticsOverview | null = null;
  healthScore: NetworkHealthScore | null = null;
  eventSummary: EventSummary | null = null;
  
  // Recent data
  recentEvents: Event[] = [];
  criticalDevices: Device[] = [];
  
  // Status
  isLoading = true;
  wsStatus: ConnectionStatus = ConnectionStatus.DISCONNECTED;
  lastRefresh: Date = new Date();
  
  // Refresh settings
  autoRefresh = true;
  refreshInterval = environment.ui.refreshInterval;

  constructor(
    private api: ApiService,
    private ws: WebsocketService,
    private notifications: NotificationService
  ) {}

  ngOnInit(): void {
    this.loadDashboardData();
    this.setupAutoRefresh();
    this.subscribeToWebSocket();
  }

  ngOnDestroy(): void {
    this.destroy$.next();
    this.destroy$.complete();
  }

  // ==================== DATA LOADING ====================

  private loadDashboardData(): void {
    this.isLoading = true;
    
    // Load statistics overview
    this.api.getStatisticsOverview().subscribe({
      next: (stats) => {
        this.statistics = stats;
        this.checkLoadingComplete();
      },
      error: (error) => {
        console.error('Error loading statistics:', error);
        this.notifications.showApiError(error);
        this.checkLoadingComplete();
      }
    });
    
    // Load network health score
    this.api.getNetworkHealthScore().subscribe({
      next: (health) => {
        this.healthScore = health;
        this.checkLoadingComplete();
      },
      error: (error) => {
        console.error('Error loading health score:', error);
        this.notifications.showApiError(error);
        this.checkLoadingComplete();
      }
    });
    
    // Load events summary
    this.api.getEventsSummary(24).subscribe({
      next: (summary) => {
        this.eventSummary = {
          total: summary.total_events,
          critical: summary.by_severity?.CRITICAL || 0,
          warning: summary.by_severity?.WARNING || 0,
          info: summary.by_severity?.INFO || 0,
          unacknowledged: summary.unacknowledged
        };
        this.checkLoadingComplete();
      },
      error: (error) => {
        console.error('Error loading event summary:', error);
        this.checkLoadingComplete();
      }
    });
    
    // Load recent events
   // NEW – remove sort_order, keep page_size
this.api.getEvents({ page_size: 10 }).subscribe({
  next: (events) => {
    this.recentEvents = events;
    this.checkLoadingComplete();
  },
  error: (error) => {
    console.error('Error loading recent events', error);
    this.checkLoadingComplete();
  }
});

    
    // Load critical devices (devices that are down)
    this.api.getDevices({ status: 'DOWN', page_size: 10 }).subscribe({
      next: (devices) => {
        this.criticalDevices = devices;
        this.checkLoadingComplete();
      },
      error: (error) => {
        console.error('Error loading critical devices:', error);
        this.checkLoadingComplete();
      }
    });
    
    this.lastRefresh = new Date();
  }

  private checkLoadingComplete(): void {
    // Simple check - in production you might want more sophisticated logic
    setTimeout(() => {
      this.isLoading = false;
    }, 500);
  }

  // ==================== AUTO REFRESH ====================

  private setupAutoRefresh(): void {
    interval(this.refreshInterval)
      .pipe(
        takeUntil(this.destroy$),
        switchMap(() => {
          if (this.autoRefresh) {
            return this.api.getStatisticsOverview();
          }
          return [];
        })
      )
      .subscribe({
        next: (stats) => {
          if (stats) {
            this.statistics = stats;
            this.lastRefresh = new Date();
          }
        }
      });
  }

  toggleAutoRefresh(): void {
    this.autoRefresh = !this.autoRefresh;
    if (this.autoRefresh) {
      this.notifications.info('Auto-refresh enabled');
    } else {
      this.notifications.info('Auto-refresh disabled');
    }
  }

  manualRefresh(): void {
    this.loadDashboardData();
    this.notifications.info('Dashboard refreshed');
  }

  // ==================== WEBSOCKET ====================

  private subscribeToWebSocket(): void {
    // Connection status
    this.ws.connectionStatus$
      .pipe(takeUntil(this.destroy$))
      .subscribe(status => {
        this.wsStatus = status;
      });
    
    // Event notifications
    this.ws.getEventNotifications()
      .pipe(takeUntil(this.destroy$))
      .subscribe((event: EventNotification) => {
        this.handleEventNotification(event);
      });
    
    // Device status updates
    this.ws.getDeviceStatusUpdates()
      .pipe(takeUntil(this.destroy$))
      .subscribe((update: DeviceStatusUpdate) => {
        this.handleDeviceStatusUpdate(update);
      });
  }

  private handleEventNotification(event: EventNotification): void {
    // Show notification for critical events
    if (event.severity === 'CRITICAL') {
      this.notifications.error(event.message, event.title);
    } else if (event.severity === 'WARNING') {
      this.notifications.warning(event.message, event.title);
    }
    
    // Refresh recent events
    this.api.getEvents({ page_size: 10 }).subscribe(events => {
      this.recentEvents = events;
    });
  }

  private handleDeviceStatusUpdate(update: DeviceStatusUpdate): void {
    // If device went down, refresh critical devices
    if (update.status === 'DOWN') {
      this.api.getDevices({ status: 'DOWN', page_size: 10 }).subscribe(devices => {
        this.criticalDevices = devices;
      });
      
      this.notifications.warning(`Device ${update.name} is DOWN`);
    }
    
    // Refresh statistics
    this.api.getStatisticsOverview().subscribe(stats => {
      this.statistics = stats;
    });
  }

  // ==================== COMPUTED PROPERTIES ====================

  get deviceStatusBreakdown(): DeviceStatusCount[] {
    if (!this.statistics) return [];
    
    const total = this.statistics.devices.total;
    if (total === 0) return [];
    
    return [
      {
        status: 'UP',
        count: this.statistics.devices.up,
        percentage: (this.statistics.devices.up / total) * 100,
        color: '#22c55e'
      },
      {
        status: 'DOWN',
        count: this.statistics.devices.down,
        percentage: (this.statistics.devices.down / total) * 100,
        color: '#ef4444'
      },
      {
        status: 'UNKNOWN',
        count: total - this.statistics.devices.up - this.statistics.devices.down,
        percentage: ((total - this.statistics.devices.up - this.statistics.devices.down) / total) * 100,
        color: '#6b7280'
      }
    ].filter(item => item.count > 0);
  }

  get deviceTypeBreakdown(): Array<{ type: string; count: number; color: string }> {
    if (!this.statistics?.devices.by_type) return [];
    
    const colors = environment.chartColors.devices;
    
    return Object.entries(this.statistics.devices.by_type).map(([type, count]) => ({
      type,
      count: count as number,
      color: colors[type as keyof typeof colors] || '#6b7280'
    }));
  }

  get healthStatusClass(): string {
    if (!this.healthScore) return 'unknown';
    
    const score = this.healthScore.overall_score;
    if (score >= 90) return 'excellent';
    if (score >= 75) return 'good';
    if (score >= 60) return 'fair';
    if (score >= 40) return 'poor';
    return 'critical';
  }

  get wsStatusIcon(): string {
    switch (this.wsStatus) {
      case ConnectionStatus.CONNECTED:
        return '🟢';
      case ConnectionStatus.CONNECTING:
      case ConnectionStatus.RECONNECTING:
        return '🟡';
      case ConnectionStatus.DISCONNECTED:
      case ConnectionStatus.ERROR:
        return '🔴';
      default:
        return '⚪';
    }
  }

  // ==================== ACTIONS ====================

  acknowledgeEvent(eventId: string): void {
    this.api.acknowledgeEvent(eventId, 'dashboard-user').subscribe({
      next: () => {
        this.notifications.success('Event acknowledged');
        this.loadDashboardData();
      },
      error: (error) => {
        this.notifications.showApiError(error);
      }
    });
  }

  pingDevice(deviceId: string): void {
    this.api.pingDevice(deviceId).subscribe({
      next: (result) => {
        const message = result.is_alive 
          ? `Device is UP (${result.response_time_ms}ms)`
          : 'Device is DOWN';
        this.notifications.success(message);
      },
      error: (error) => {
        this.notifications.showApiError(error);
      }
    });
  }

  runMonitoringCycle(): void {
    this.api.runMonitoringCycle().subscribe({
      next: () => {
        this.notifications.info('Monitoring cycle started');
      },
      error: (error) => {
        this.notifications.showApiError(error);
      }
    });
  }

  // ==================== UTILITIES ====================

  getEventSeverityClass(severity: string): string {
    return `severity-${severity.toLowerCase()}`;
  }

  getStatusBadgeClass(status: string): string {
    return `status-${status.toLowerCase()}`;
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
}