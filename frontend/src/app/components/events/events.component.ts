import { Component, OnInit, OnDestroy } from '@angular/core';
import { Subject } from 'rxjs';
import { takeUntil, debounceTime } from 'rxjs/operators';
import { ApiService, Event, EventType, EventSeverity } from '../../services/api.service';
import { WebsocketService, EventNotification } from '../../services/websocket.service';
import { NotificationService } from '../../services/notification.service';

@Component({
  selector: 'app-events',
  templateUrl: './events.component.html',
  styleUrls: ['./events.component.scss']
})
export class EventsComponent implements OnInit, OnDestroy {
  private destroy$ = new Subject<void>();
  private searchSubject$ = new Subject<string>();

  events: Event[] = [];
  searchTerm = '';
  selectedSeverity: EventSeverity | '' = '';
  selectedType: EventType | '' = '';
  showAcknowledgedOnly = false;
  showUnacknowledgedOnly = false;

  currentPage = 1;
  pageSize = 20;
  totalEvents = 0;

  isLoading = false;
  selectedEvents: string[] = [];

  eventTypes: EventType[] = [
    'DEVICE_UP',
    'DEVICE_DOWN',
    'LINK_UP',
    'LINK_DOWN',
    'PORT_UP',
    'PORT_DOWN',
    'HIGH_LATENCY',
    'PACKET_LOSS',
    'CONFIG_CHANGE',
    'SNMP_TRAP',
    'ALERT',
    'OTHER'
  ];
  eventSeverities: EventSeverity[] = ['CRITICAL', 'WARNING', 'INFO'];

  constructor(
    private api: ApiService,
    private ws: WebsocketService,
    private notifications: NotificationService
  ) {}

  ngOnInit(): void {
    this.loadEvents();
    this.setupSearch();
    this.subscribeToUpdates();
  }

  ngOnDestroy(): void {
    this.destroy$.next();
    this.destroy$.complete();
  }

  // --- Pagination helpers ---

  get totalPages(): number {
    if (this.totalEvents === 0) {
      return 1;
    }
    return Math.max(1, Math.ceil(this.totalEvents / this.pageSize));
  }

  previousPage(): void {
    if (this.currentPage > 1) {
      this.currentPage--;
      this.loadEvents();
    }
  }

  nextPage(): void {
    if (this.currentPage < this.totalPages) {
      this.currentPage++;
      this.loadEvents();
    }
  }

  // --- Data loading ---

loadEvents(): void {
  this.isLoading = true;

  const params: any = {
    page: this.currentPage,
    page_size: this.pageSize
  };

  if (this.selectedSeverity) params.severity = this.selectedSeverity;
  if (this.selectedType) params.event_type = this.selectedType;
  if (this.showAcknowledgedOnly) params.acknowledged = true;
  if (this.showUnacknowledgedOnly) params.acknowledged = false;

  this.api.getEvents(params).subscribe({
    next: (events) => {
      this.events = events;
      this.totalEvents = Math.max(this.totalEvents, events.length);
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
      .pipe(debounceTime(300), takeUntil(this.destroy$))
      .subscribe(() => this.loadEvents());
  }

  private subscribeToUpdates(): void {
    this.ws.getEventNotifications()
      .pipe(takeUntil(this.destroy$))
      .subscribe((notification: EventNotification) => {
        this.loadEvents();
      });
  }

  onFilterChange(): void {
    this.currentPage = 1;
    this.loadEvents();
  }

  acknowledgeEvent(event: Event): void {
    this.api.acknowledgeEvent(event.id, 'events-user').subscribe({
      next: () => {
        event.acknowledged = true;
        this.notifications.success('Event acknowledged');
      },
      error: (error) => this.notifications.showApiError(error)
    });
  }

  bulkAcknowledge(): void {
    if (this.selectedEvents.length === 0) return;

    this.api.bulkAcknowledgeEvents(this.selectedEvents, 'events-user').subscribe({
      next: () => {
        this.selectedEvents = [];
        this.loadEvents();
        this.notifications.success('Events acknowledged');
      },
      error: (error) => this.notifications.showApiError(error)
    });
  }

  toggleEventSelection(eventId: string): void {
    const index = this.selectedEvents.indexOf(eventId);
    if (index > -1) {
      this.selectedEvents.splice(index, 1);
    } else {
      this.selectedEvents.push(eventId);
    }
  }

  getSeverityClass(severity: string): string {
    return `severity-${severity.toLowerCase()}`;
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
