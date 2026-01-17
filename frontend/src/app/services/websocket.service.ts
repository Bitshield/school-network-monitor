import { Injectable, OnDestroy } from '@angular/core';
import { webSocket, WebSocketSubject } from 'rxjs/webSocket';
import { Observable, Subject, timer, EMPTY, interval } from 'rxjs';
import { retryWhen, tap, delayWhen, catchError, takeUntil } from 'rxjs/operators';
import { environment } from '../../environments/environment';

// ==================== WEBSOCKET MESSAGE TYPES ====================

export interface WebSocketMessage {
  type: 'TOPOLOGY_UPDATE' | 'DEVICE_STATUS' | 'LINK_STATUS' | 'PORT_STATUS' | 
        'EVENT_NOTIFICATION' | 'MONITORING_RESULT' | 'CABLE_HEALTH_UPDATE' | 
        'DISCOVERY_COMPLETE' | 'PONG' | 'ERROR';
  data: any;
  timestamp?: string;
}

export interface TopologyUpdate {
  devices: any[];
  links: any[];
  ports: any[];
  statistics: {
    total_devices: number;
    devices_up: number;
    devices_down: number;
    total_links: number;
    links_up: number;
    links_degraded: number;
    total_ports: number;
    ports_up: number;
  };
}

export interface DeviceStatusUpdate {
  device_id: string;
  status: 'UP' | 'DOWN' | 'UNKNOWN';
  ip: string;
  name: string;
  response_time_ms: number | null;
  timestamp: string;
}

export interface LinkStatusUpdate {
  link_id: string;
  status: 'UP' | 'DOWN' | 'DEGRADED' | 'UNKNOWN';
  source_device_id: string;
  target_device_id: string;
  latency_ms: number | null;
  packet_loss_percent: number | null;
  timestamp: string;
}

export interface PortStatusUpdate {
  port_id: string;
  device_id: string;
  port_number: number;
  status: 'UP' | 'DOWN' | 'DISABLED' | 'TESTING' | 'UNKNOWN';
  is_up: boolean;
  timestamp: string;
}

export interface EventNotification {
  id: string;
  event_type: string;
  severity: 'CRITICAL' | 'WARNING' | 'INFO';
  title: string;
  message: string;
  device_id: string | null;
  link_id: string | null;
  port_id: string | null;
  timestamp: string;
}

export interface MonitoringResult {
  device_id: string;
  device_name: string;
  ip: string;
  status: 'UP' | 'DOWN' | 'UNKNOWN';
  response_time_ms: number | null;
  timestamp: string;
  checks_performed: string[];
}

export interface CableHealthUpdate {
  link_id: string;
  health_score: number;
  status: 'GOOD' | 'DEGRADED' | 'POOR' | 'CRITICAL' | 'UNKNOWN';
  signal_strength_dbm: number | null;
  timestamp: string;
}

export enum ConnectionStatus {
  CONNECTED = 'connected',
  DISCONNECTED = 'disconnected',
  CONNECTING = 'connecting',
  RECONNECTING = 'reconnecting',
  ERROR = 'error'
}

// ==================== WEBSOCKET SERVICE ====================

@Injectable({
  providedIn: 'root'
})
export class WebsocketService implements OnDestroy {
  private socket$: WebSocketSubject<WebSocketMessage> | null = null;
  private messagesSubject$ = new Subject<WebSocketMessage>();
  private connectionStatusSubject$ = new Subject<ConnectionStatus>();
  private destroy$ = new Subject<void>();
  
  public messages$ = this.messagesSubject$.asObservable();
  public connectionStatus$ = this.connectionStatusSubject$.asObservable();

  private wsUrl = environment.wsUrl;
  private reconnectInterval = environment.websocket.reconnectInterval;
  private maxReconnectAttempts = environment.websocket.maxReconnectAttempts;
  private heartbeatInterval = environment.websocket.heartbeatInterval;
  
  private reconnectAttempts = 0;
  private heartbeatTimer: any;
  private isManualDisconnect = false;

  constructor() {
    this.connect();
    this.startHeartbeat();
  }

  ngOnDestroy(): void {
    this.isManualDisconnect = true;
    this.destroy$.next();
    this.destroy$.complete();
    this.stopHeartbeat();
    this.disconnect();
  }

  // ==================== CONNECTION MANAGEMENT ====================

  /**
   * Establish WebSocket connection
   */
  public connect(): void {
    if (this.socket$ && !this.socket$.closed) {
      console.log('[WebSocket] Already connected');
      return;
    }

    this.connectionStatusSubject$.next(ConnectionStatus.CONNECTING);
    console.log('[WebSocket] Connecting to:', this.wsUrl);
    
    this.socket$ = webSocket<WebSocketMessage>({
      url: this.wsUrl,
      openObserver: {
        next: () => {
          console.log('[WebSocket] Connection established');
          this.connectionStatusSubject$.next(ConnectionStatus.CONNECTED);
          this.reconnectAttempts = 0;
          this.isManualDisconnect = false;
        }
      },
      closeObserver: {
        next: (event) => {
          console.log('[WebSocket] Connection closed', event);
          this.connectionStatusSubject$.next(ConnectionStatus.DISCONNECTED);
          this.socket$ = null;
          
          if (!this.isManualDisconnect) {
            this.reconnect();
          }
        }
      },
      closingObserver: {
        next: () => {
          console.log('[WebSocket] Connection closing...');
        }
      }
    });

    this.socket$
      .pipe(
        takeUntil(this.destroy$),
        tap((message: WebSocketMessage) => {
          console.log('[WebSocket] Received:', message.type, message);
          this.messagesSubject$.next(message);
        }),
        catchError((error) => {
          console.error('[WebSocket] Error:', error);
          this.connectionStatusSubject$.next(ConnectionStatus.ERROR);
          return EMPTY;
        })
      )
      .subscribe({
        error: (err) => {
          console.error('[WebSocket] Subscription error:', err);
          if (!this.isManualDisconnect) {
            this.reconnect();
          }
        }
      });
  }

  /**
   * Reconnect with exponential backoff
   */
  private reconnect(): void {
    if (this.reconnectAttempts >= this.maxReconnectAttempts) {
      console.error('[WebSocket] Max reconnection attempts reached');
      this.connectionStatusSubject$.next(ConnectionStatus.ERROR);
      return;
    }

    this.reconnectAttempts++;
    const delay = this.reconnectInterval * Math.pow(1.5, this.reconnectAttempts - 1);
    
    console.log(
      `[WebSocket] Reconnecting in ${delay}ms (attempt ${this.reconnectAttempts}/${this.maxReconnectAttempts})`
    );
    
    this.connectionStatusSubject$.next(ConnectionStatus.RECONNECTING);

    setTimeout(() => {
      if (!this.isManualDisconnect) {
        this.connect();
      }
    }, delay);
  }

  /**
   * Disconnect WebSocket
   */
  public disconnect(): void {
    this.isManualDisconnect = true;
    this.stopHeartbeat();
    
    if (this.socket$) {
      console.log('[WebSocket] Disconnecting...');
      this.socket$.complete();
      this.socket$ = null;
    }
    
    this.connectionStatusSubject$.next(ConnectionStatus.DISCONNECTED);
  }

  /**
   * Reconnect manually
   */
  public reconnectManually(): void {
    this.disconnect();
    this.isManualDisconnect = false;
    this.reconnectAttempts = 0;
    setTimeout(() => this.connect(), 1000);
  }

  // ==================== HEARTBEAT ====================

  /**
   * Start heartbeat to keep connection alive
   */
  private startHeartbeat(): void {
    this.stopHeartbeat();
    
    this.heartbeatTimer = setInterval(() => {
      if (this.isConnected()) {
        this.sendPing();
      }
    }, this.heartbeatInterval);
  }

  /**
   * Stop heartbeat
   */
  private stopHeartbeat(): void {
    if (this.heartbeatTimer) {
      clearInterval(this.heartbeatTimer);
      this.heartbeatTimer = null;
    }
  }

  // ==================== MESSAGE FILTERING ====================

  /**
   * Get messages of a specific type
   */
  public getMessagesByType<T = any>(type: WebSocketMessage['type']): Observable<T> {
    return new Observable<T>(observer => {
      const subscription = this.messages$.subscribe({
        next: (message) => {
          if (message.type === type) {
            observer.next(message.data as T);
          }
        },
        error: (err) => observer.error(err),
        complete: () => observer.complete()
      });

      return () => subscription.unsubscribe();
    });
  }

  /**
   * Get topology updates
   */
  public getTopologyUpdates(): Observable<TopologyUpdate> {
    return this.getMessagesByType<TopologyUpdate>('TOPOLOGY_UPDATE');
  }

  /**
   * Get device status updates
   */
  public getDeviceStatusUpdates(): Observable<DeviceStatusUpdate> {
    return this.getMessagesByType<DeviceStatusUpdate>('DEVICE_STATUS');
  }

  /**
   * Get link status updates
   */
  public getLinkStatusUpdates(): Observable<LinkStatusUpdate> {
    return this.getMessagesByType<LinkStatusUpdate>('LINK_STATUS');
  }

  /**
   * Get port status updates
   */
  public getPortStatusUpdates(): Observable<PortStatusUpdate> {
    return this.getMessagesByType<PortStatusUpdate>('PORT_STATUS');
  }

  /**
   * Get event notifications
   */
  public getEventNotifications(): Observable<EventNotification> {
    return this.getMessagesByType<EventNotification>('EVENT_NOTIFICATION');
  }

  /**
   * Get monitoring results
   */
  public getMonitoringResults(): Observable<MonitoringResult> {
    return this.getMessagesByType<MonitoringResult>('MONITORING_RESULT');
  }

  /**
   * Get cable health updates
   */
  public getCableHealthUpdates(): Observable<CableHealthUpdate> {
    return this.getMessagesByType<CableHealthUpdate>('CABLE_HEALTH_UPDATE');
  }

  /**
   * Get discovery complete notifications
   */
  public getDiscoveryComplete(): Observable<any> {
    return this.getMessagesByType<any>('DISCOVERY_COMPLETE');
  }

  // ==================== SEND MESSAGES ====================

  /**
   * Send a message through WebSocket
   */
  public send(message: any): void {
    if (this.socket$ && !this.socket$.closed) {
      try {
        this.socket$.next(message);
        console.log('[WebSocket] Sent:', message);
      } catch (error) {
        console.error('[WebSocket] Send error:', error);
      }
    } else {
      console.warn('[WebSocket] Cannot send message - not connected');
    }
  }

  /**
   * Send ping to keep connection alive
   */
  public sendPing(): void {
    this.send({ type: 'PING', data: { timestamp: new Date().toISOString() } });
  }

  /**
   * Request full topology update
   */
  public requestTopologyUpdate(): void {
    this.send({ type: 'REQUEST_TOPOLOGY', data: {} });
  }

  /**
   * Subscribe to device updates
   */
  public subscribeToDevice(deviceId: string): void {
    this.send({ type: 'SUBSCRIBE_DEVICE', data: { device_id: deviceId } });
  }

  /**
   * Unsubscribe from device updates
   */
  public unsubscribeFromDevice(deviceId: string): void {
    this.send({ type: 'UNSUBSCRIBE_DEVICE', data: { device_id: deviceId } });
  }

  /**
   * Subscribe to link updates
   */
  public subscribeToLink(linkId: string): void {
    this.send({ type: 'SUBSCRIBE_LINK', data: { link_id: linkId } });
  }

  /**
   * Unsubscribe from link updates
   */
  public unsubscribeFromLink(linkId: string): void {
    this.send({ type: 'UNSUBSCRIBE_LINK', data: { link_id: linkId } });
  }

  // ==================== UTILITY METHODS ====================

  /**
   * Check if WebSocket is connected
   */
  public isConnected(): boolean {
    return this.socket$ !== null && !this.socket$.closed;
  }

  /**
   * Get current connection status
   */
  public getConnectionStatus(): ConnectionStatus {
    if (!this.socket$) {
      return ConnectionStatus.DISCONNECTED;
    }
    if (this.socket$.closed) {
      return ConnectionStatus.DISCONNECTED;
    }
    if (this.reconnectAttempts > 0) {
      return ConnectionStatus.RECONNECTING;
    }
    return ConnectionStatus.CONNECTED;
  }

  /**
   * Get reconnection attempts
   */
  public getReconnectAttempts(): number {
    return this.reconnectAttempts;
  }

  /**
   * Reset reconnection attempts
   */
  public resetReconnectAttempts(): void {
    this.reconnectAttempts = 0;
  }
}