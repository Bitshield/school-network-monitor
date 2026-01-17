import { Injectable } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../environments/environment';

// ==================== BASE TYPES ====================

export interface PaginationParams {
  page?: number;
  page_size?: number;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  page_size: number;
  pages: number;
}

// ==================== DEVICE TYPES ====================

export type DeviceStatus = 'UP' | 'DOWN' | 'UNKNOWN';
export type DeviceType = 'router' | 'switch' | 'pc' | 'server' | 'printer' | 'access_point';

export interface Device {
  id: string;
  name: string;
  ip: string | null;
  mac: string | null;
  hostname: string | null;
  device_type: DeviceType;
  location: string | null;
  description: string | null;
  manufacturer: string | null;
  model: string | null;
  serial_number: string | null;
  firmware_version: string | null;
  status: DeviceStatus;
  is_monitored: boolean;
  snmp_enabled: boolean;
  snmp_community: string | null;
  vlan_id: number | null;
  last_seen: string | null;
  created_at: string;
  updated_at: string;
}

export interface DeviceCreate {
  name: string;
  ip?: string;
  mac?: string;
  hostname?: string;
  device_type: DeviceType;
  location?: string;
  description?: string;
  manufacturer?: string;
  model?: string;
  serial_number?: string;
  firmware_version?: string;
  is_monitored?: boolean;
  snmp_enabled?: boolean;
  snmp_community?: string;
  vlan_id?: number;
}

export interface DeviceUpdate {
  name?: string;
  ip?: string;
  mac?: string;
  hostname?: string;
  device_type?: DeviceType;
  location?: string;
  description?: string;
  manufacturer?: string;
  model?: string;
  serial_number?: string;
  firmware_version?: string;
  is_monitored?: boolean;
  snmp_enabled?: boolean;
  snmp_community?: string;
  vlan_id?: number;
}

// ==================== PORT TYPES ====================

export type PortStatus = 'UP' | 'DOWN' | 'DISABLED' | 'TESTING' | 'UNKNOWN';

export interface Port {
  id: string;
  device_id: string;
  port_number: number;
  port_name: string;
  port_type: string | null;
  status: PortStatus;
  is_up: boolean;
  admin_status: string | null;
  speed_mbps: number | null;
  duplex: string | null;
  mtu: number | null;
  mac_address: string | null;
  vlan_id: number | null;
  description: string | null;
  rx_bytes: number;
  tx_bytes: number;
  rx_packets: number;
  tx_packets: number;
  rx_errors: number;
  tx_errors: number;
  rx_dropped: number;
  tx_dropped: number;
  crc_errors: number;
  frame_errors: number;
  collision_count: number;
  last_check: string | null;
  last_seen: string | null;
  created_at: string;
  updated_at: string;
}

export interface PortCreate {
  device_id: string;
  port_number: number;
  port_name: string;
  port_type?: string;
  admin_status?: string;
  speed_mbps?: number;
  duplex?: string;
  mtu?: number;
  mac_address?: string;
  vlan_id?: number;
  description?: string;
}

export interface PortUpdate {
  port_name?: string;
  port_type?: string;
  admin_status?: string;
  speed_mbps?: number;
  duplex?: string;
  mtu?: number;
  mac_address?: string;
  vlan_id?: number;
  description?: string;
}

// ==================== LINK TYPES ====================

export type LinkStatus = 'UP' | 'DOWN' | 'DEGRADED' | 'UNKNOWN';

export interface Link {
  id: string;
  source_device_id: string;
  target_device_id: string;
  source_port_id: string | null;
  target_port_id: string | null;
  link_type: string | null;
  status: LinkStatus;
  bandwidth_mbps: number | null;
  latency_ms: number | null;
  packet_loss_percent: number | null;
  utilization_percent: number | null;
  description: string | null;
  last_check: string | null;
  last_seen: string | null;
  created_at: string;
  updated_at: string;
}

export interface LinkCreate {
  source_device_id: string;
  target_device_id: string;
  source_port_id?: string;
  target_port_id?: string;
  link_type?: string;
  bandwidth_mbps?: number;
  description?: string;
}

export interface LinkUpdate {
  source_port_id?: string;
  target_port_id?: string;
  link_type?: string;
  bandwidth_mbps?: number;
  description?: string;
}

// ==================== EVENT TYPES ====================

export type EventType = 'DEVICE_UP' | 'DEVICE_DOWN' | 'LINK_UP' | 'LINK_DOWN' | 'PORT_UP' | 'PORT_DOWN' | 
  'HIGH_LATENCY' | 'PACKET_LOSS' | 'CONFIG_CHANGE' | 'SNMP_TRAP' | 'ALERT' | 'OTHER';
export type EventSeverity = 'CRITICAL' | 'WARNING' | 'INFO';

export interface Event {
  id: string;
  event_type: EventType;
  severity: EventSeverity;
  title: string;
  message: string;
  device_id: string | null;
  port_id: string | null;
  link_id: string | null;
  acknowledged: boolean;
  acknowledged_by: string | null;
  acknowledged_at: string | null;
  resolved: boolean;
  resolved_by: string | null;
  resolved_at: string | null;
  resolution_notes: string | null;
  occurrence_count: number;
  first_occurred_at: string;
  last_occurred_at: string;
  metadata: any;
  created_at: string;
  updated_at: string;
}

export interface EventCreate {
  event_type: EventType;
  severity: EventSeverity;
  title: string;
  message: string;
  device_id?: string;
  port_id?: string;
  link_id?: string;
  metadata?: any;
}

// ==================== CABLE HEALTH TYPES ====================

export type CableHealthStatus = 'GOOD' | 'DEGRADED' | 'POOR' | 'CRITICAL' | 'UNKNOWN';

export interface CableHealthMetrics {
  id: string;
  link_id: string;
  status: CableHealthStatus;
  health_score: number;
  signal_strength_dbm: number | null;
  noise_level_dbm: number | null;
  snr_db: number | null;
  attenuation_db: number | null;
  impedance_ohms: number | null;
  capacitance_pf: number | null;
  length_meters: number | null;
  test_date: string;
  measured_at: string;
  created_at: string;
  updated_at: string;
}

export interface CableHealthCreate {
  link_id: string;
  health_score: number;
  signal_strength_dbm?: number;
  noise_level_dbm?: number;
  snr_db?: number;
  attenuation_db?: number;
  impedance_ohms?: number;
  capacitance_pf?: number;
  length_meters?: number;
}

export interface CableHealthTestRequest {
  link_id: string;
}

export interface CableHealthTestResult {
  link_id: string;
  test_passed: boolean;
  status: CableHealthStatus;
  signal_quality: number | null;
  issues_found: string[];
  recommendations: string[];
  test_duration: number;
  tested_at: string;
}

// ==================== DISCOVERY TYPES ====================

export interface DiscoveredDevice {
  ip: string;
  mac: string | null;
  hostname: string | null;
  manufacturer: string | null;
  is_alive: boolean;
  response_time_ms: number | null;
}

export interface ScanResult {
  network_range: string;
  devices_found: number;
  devices: DiscoveredDevice[];
  save_result?: any;
}

// ==================== SNMP TYPES ====================

export interface SNMPSystemInfo {
  sysDescr: string | null;
  sysObjectID: string | null;
  sysUpTime: number | null;
  sysContact: string | null;
  sysName: string | null;
  sysLocation: string | null;
}

export interface SNMPInterface {
  ifIndex: number;
  ifDescr: string;
  ifType: number;
  ifMtu: number;
  ifSpeed: number;
  ifPhysAddress: string;
  ifAdminStatus: number;
  ifOperStatus: number;
}

// ==================== STATISTICS TYPES ====================

export interface StatisticsOverview {
  devices: {
    total: number;
    up: number;
    down: number;
    monitored: number;
    by_type: { [key: string]: number };
  };
  links: {
    total: number;
    up: number;
    degraded: number;
  };
  ports: {
    total: number;
    up: number;
  };
  events: {
    last_24h: number;
    critical_24h: number;
  };
}

export interface NetworkHealthScore {
  overall_score: number;
  status: 'EXCELLENT' | 'GOOD' | 'FAIR' | 'POOR' | 'CRITICAL';
  components: {
    device_health: number;
    link_health: number;
    event_impact: number;
  };
  metrics: {
    devices_up: number;
    total_devices: number;
    links_up: number;
    total_links: number;
    critical_events_1h: number;
  };
}

// ==================== VALIDATION TYPES ====================

export interface ValidationResult {
  valid: boolean;
  error?: string;
  normalized?: string;
}

// ==================== SERVICE ====================

@Injectable({
  providedIn: 'root'
})
export class ApiService {
  private baseUrl = environment.apiUrl;

  constructor(private http: HttpClient) {}

  // ==================== DEVICE ENDPOINTS ====================

  getDevices(params?: {
    page?: number;
    page_size?: number;
    search?: string;
    status?: DeviceStatus;
    device_type?: DeviceType;
    is_monitored?: boolean;
    sort_by?: string;
    sort_order?: 'asc' | 'desc';
  }): Observable<Device[]> {
    let httpParams = new HttpParams();
    if (params) {
      Object.entries(params).forEach(([key, value]) => {
        if (value !== undefined && value !== null) {
          httpParams = httpParams.set(key, value.toString());
        }
      });
    }
    return this.http.get<Device[]>(`${this.baseUrl}/devices`, { params: httpParams });
  }

  getDeviceCount(status?: DeviceStatus, device_type?: DeviceType): Observable<{ count: number }> {
    let params = new HttpParams();
    if (status) params = params.set('status', status);
    if (device_type) params = params.set('device_type', device_type);
    return this.http.get<{ count: number }>(`${this.baseUrl}/devices/count`, { params });
  }

  getDevice(id: string): Observable<Device> {
    return this.http.get<Device>(`${this.baseUrl}/devices/${id}`);
  }

  createDevice(device: DeviceCreate): Observable<Device> {
    return this.http.post<Device>(`${this.baseUrl}/devices`, device);
  }

  updateDevice(id: string, device: DeviceUpdate): Observable<Device> {
    return this.http.put<Device>(`${this.baseUrl}/devices/${id}`, device);
  }

  deleteDevice(id: string): Observable<void> {
    return this.http.delete<void>(`${this.baseUrl}/devices/${id}`);
  }

  pingDevice(id: string): Observable<any> {
    return this.http.post(`${this.baseUrl}/devices/${id}/ping`, {});
  }

  getDevicePorts(id: string): Observable<Port[]> {
    return this.http.get<Port[]>(`${this.baseUrl}/devices/${id}/ports`);
  }

  getDeviceLinks(id: string): Observable<Link[]> {
    return this.http.get<Link[]>(`${this.baseUrl}/devices/${id}/links`);
  }

  getDeviceEvents(id: string, limit: number = 50): Observable<Event[]> {
    return this.http.get<Event[]>(`${this.baseUrl}/devices/${id}/events`, {
      params: { limit: limit.toString() }
    });
  }

  // ==================== PORT ENDPOINTS ====================

  getPorts(params?: {
    page?: number;
    page_size?: number;
    device_id?: string;
    status?: PortStatus;
  }): Observable<Port[]> {
    let httpParams = new HttpParams();
    if (params) {
      Object.entries(params).forEach(([key, value]) => {
        if (value !== undefined && value !== null) {
          httpParams = httpParams.set(key, value.toString());
        }
      });
    }
    return this.http.get<Port[]>(`${this.baseUrl}/ports`, { params: httpParams });
  }

  getPort(id: string): Observable<Port> {
    return this.http.get<Port>(`${this.baseUrl}/ports/${id}`);
  }

  createPort(port: PortCreate): Observable<Port> {
    return this.http.post<Port>(`${this.baseUrl}/ports`, port);
  }

  updatePort(id: string, port: PortUpdate): Observable<Port> {
    return this.http.put<Port>(`${this.baseUrl}/ports/${id}`, port);
  }

  deletePort(id: string): Observable<void> {
    return this.http.delete<void>(`${this.baseUrl}/ports/${id}`);
  }

  getPortStatistics(id: string): Observable<any> {
    return this.http.get(`${this.baseUrl}/ports/${id}/statistics`);
  }

  // ==================== LINK ENDPOINTS ====================

  getLinks(params?: {
    page?: number;
    page_size?: number;
    status?: LinkStatus;
    device_id?: string;
  }): Observable<Link[]> {
    let httpParams = new HttpParams();
    if (params) {
      Object.entries(params).forEach(([key, value]) => {
        if (value !== undefined && value !== null) {
          httpParams = httpParams.set(key, value.toString());
        }
      });
    }
    return this.http.get<Link[]>(`${this.baseUrl}/links`, { params: httpParams });
  }

  getLink(id: string): Observable<Link> {
    return this.http.get<Link>(`${this.baseUrl}/links/${id}`);
  }

  createLink(link: LinkCreate): Observable<Link> {
    return this.http.post<Link>(`${this.baseUrl}/links`, link);
  }

  updateLink(id: string, link: LinkUpdate): Observable<Link> {
    return this.http.put<Link>(`${this.baseUrl}/links/${id}`, link);
  }

  deleteLink(id: string): Observable<void> {
    return this.http.delete<void>(`${this.baseUrl}/links/${id}`);
  }

  testLink(id: string): Observable<any> {
    return this.http.post(`${this.baseUrl}/links/${id}/test`, {});
  }

  getLinkHealthHistory(id: string, hours: number = 24): Observable<CableHealthMetrics[]> {
    return this.http.get<CableHealthMetrics[]>(`${this.baseUrl}/links/${id}/health-history`, {
      params: { hours: hours.toString() }
    });
  }

  // ==================== EVENT ENDPOINTS ====================

  getEvents(params?: {
    page?: number;
    page_size?: number;
    event_type?: EventType;
    severity?: EventSeverity;
    device_id?: string;
    acknowledged?: boolean;
    resolved?: boolean;
    start_date?: string;
    end_date?: string;
  }): Observable<Event[]> {
    let httpParams = new HttpParams();
    if (params) {
      Object.entries(params).forEach(([key, value]) => {
        if (value !== undefined && value !== null) {
          httpParams = httpParams.set(key, value.toString());
        }
      });
    }
    return this.http.get<Event[]>(`${this.baseUrl}/events`, { params: httpParams });
  }

  getUnacknowledgedEvents(limit: number = 100): Observable<Event[]> {
    return this.http.get<Event[]>(`${this.baseUrl}/events/unacknowledged`, {
      params: { limit: limit.toString() }
    });
  }

  getCriticalEvents(hours: number = 24): Observable<Event[]> {
    return this.http.get<Event[]>(`${this.baseUrl}/events/critical`, {
      params: { hours: hours.toString() }
    });
  }

  getEventsSummary(hours: number = 24): Observable<any> {
    return this.http.get(`${this.baseUrl}/events/summary`, {
      params: { hours: hours.toString() }
    });
  }

  getEvent(id: string): Observable<Event> {
    return this.http.get<Event>(`${this.baseUrl}/events/${id}`);
  }

  createEvent(event: EventCreate): Observable<Event> {
    return this.http.post<Event>(`${this.baseUrl}/events`, event);
  }

  acknowledgeEvent(id: string, acknowledgedBy: string, notes?: string): Observable<any> {
    return this.http.patch(`${this.baseUrl}/events/${id}/acknowledge`, {
      acknowledged_by: acknowledgedBy,
      notes
    });
  }

  resolveEvent(id: string, resolvedBy: string, resolutionNotes?: string): Observable<any> {
    return this.http.patch(`${this.baseUrl}/events/${id}/resolve`, {
      resolved_by: resolvedBy,
      resolution_notes: resolutionNotes
    });
  }

  bulkAcknowledgeEvents(eventIds: string[], acknowledgedBy: string, notes?: string): Observable<any> {
    return this.http.post(`${this.baseUrl}/events/bulk-acknowledge`, {
      event_ids: eventIds,
      acknowledged_by: acknowledgedBy,
      notes
    });
  }

  deleteEvent(id: string): Observable<void> {
    return this.http.delete<void>(`${this.baseUrl}/events/${id}`);
  }

  // ==================== CABLE HEALTH ENDPOINTS ====================

  getCableHealthMetrics(params?: {
    page?: number;
    page_size?: number;
    link_id?: string;
    status?: CableHealthStatus;
  }): Observable<CableHealthMetrics[]> {
    let httpParams = new HttpParams();
    if (params) {
      Object.entries(params).forEach(([key, value]) => {
        if (value !== undefined && value !== null) {
          httpParams = httpParams.set(key, value.toString());
        }
      });
    }
    return this.http.get<CableHealthMetrics[]>(`${this.baseUrl}/cable-health`, { params: httpParams });
  }

  getUnhealthyCables(threshold: number = 70): Observable<any> {
    return this.http.get(`${this.baseUrl}/cable-health/unhealthy`, {
      params: { threshold: threshold.toString() }
    });
  }

  getCableHealthMetric(id: string): Observable<CableHealthMetrics> {
    return this.http.get<CableHealthMetrics>(`${this.baseUrl}/cable-health/${id}`);
  }

  testCableHealth(request: CableHealthTestRequest): Observable<CableHealthTestResult> {
    return this.http.post<CableHealthTestResult>(`${this.baseUrl}/cable-health/test`, request);
  }

  getLinkCableHealthHistory(linkId: string, hours: number = 24): Observable<any> {
    return this.http.get(`${this.baseUrl}/cable-health/link/${linkId}/history`, {
      params: { hours: hours.toString() }
    });
  }

  getLinkLatestHealth(linkId: string): Observable<CableHealthMetrics> {
    return this.http.get<CableHealthMetrics>(`${this.baseUrl}/cable-health/link/${linkId}/latest`);
  }

  createCableHealthMetric(metric: CableHealthCreate): Observable<CableHealthMetrics> {
    return this.http.post<CableHealthMetrics>(`${this.baseUrl}/cable-health`, metric);
  }

  deleteCableHealthMetric(id: string): Observable<void> {
    return this.http.delete<void>(`${this.baseUrl}/cable-health/${id}`);
  }

  // ==================== MONITORING ENDPOINTS ====================

  getMonitoringStatus(): Observable<any> {
    return this.http.get(`${this.baseUrl}/monitoring/status`);
  }

  runMonitoringCycle(): Observable<any> {
    return this.http.post(`${this.baseUrl}/monitoring/run-cycle`, {});
  }

  checkAllDevices(): Observable<any> {
    return this.http.post(`${this.baseUrl}/monitoring/devices/check-all`, {});
  }

  checkAllLinks(): Observable<any> {
    return this.http.post(`${this.baseUrl}/monitoring/links/check-all`, {});
  }

  getHealthSummary(): Observable<any> {
    return this.http.get(`${this.baseUrl}/monitoring/health-summary`);
  }

  // ==================== DISCOVERY ENDPOINTS ====================

  scanNetwork(networkRange: string, saveResults: boolean = true): Observable<ScanResult> {
    return this.http.post<ScanResult>(`${this.baseUrl}/discovery/scan`, null, {
      params: {
        network_range: networkRange,
        save_results: saveResults.toString()
      }
    });
  }

  scanNetworkBackground(networkRange: string): Observable<any> {
    return this.http.post(`${this.baseUrl}/discovery/scan-background`, null, {
      params: { network_range: networkRange }
    });
  }

  scanSingleDevice(ip: string, saveResult: boolean = true): Observable<any> {
    return this.http.post(`${this.baseUrl}/discovery/scan-device/${ip}`, null, {
      params: { save_result: saveResult.toString() }
    });
  }

  arpScan(networkRange: string): Observable<any> {
    return this.http.get(`${this.baseUrl}/discovery/arp-scan`, {
      params: { network_range: networkRange }
    });
  }

  pingSweep(ips: string[]): Observable<any> {
    return this.http.post(`${this.baseUrl}/discovery/ping-sweep`, { ips });
  }

  // ==================== SNMP ENDPOINTS ====================

  getDeviceSNMPInfo(deviceId: string, community?: string): Observable<SNMPSystemInfo> {
    let params = new HttpParams();
    if (community) params = params.set('community', community);
    return this.http.get<SNMPSystemInfo>(`${this.baseUrl}/snmp/device/${deviceId}/info`, { params });
  }

  getDeviceSNMPInterfaces(deviceId: string, community?: string): Observable<any> {
    let params = new HttpParams();
    if (community) params = params.set('community', community);
    return this.http.get(`${this.baseUrl}/snmp/device/${deviceId}/interfaces`, { params });
  }

  querySNMPOID(ip: string, oid: string, community?: string): Observable<any> {
    let params = new HttpParams().set('community', community || 'public');
    return this.http.post(`${this.baseUrl}/snmp/query-oid`, { ip, oid }, { params });
  }

  walkSNMPOID(ip: string, baseOid: string, community?: string, maxRows: number = 100): Observable<any> {
    let params = new HttpParams()
      .set('community', community || 'public')
      .set('max_rows', maxRows.toString());
    return this.http.post(`${this.baseUrl}/snmp/walk-oid`, { ip, base_oid: baseOid }, { params });
  }

  discoverDevicesSNMP(ips: string[], community?: string): Observable<any> {
    let params = new HttpParams().set('community', community || 'public');
    return this.http.post(`${this.baseUrl}/snmp/discover-devices`, { ips }, { params });
  }

  // ==================== STATISTICS ENDPOINTS ====================

  getStatisticsOverview(): Observable<StatisticsOverview> {
    return this.http.get<StatisticsOverview>(`${this.baseUrl}/statistics/overview`);
  }

  getDevicesByType(): Observable<any> {
    return this.http.get(`${this.baseUrl}/statistics/devices/by-type`);
  }

  getDevicesByStatus(): Observable<any> {
    return this.http.get(`${this.baseUrl}/statistics/devices/by-status`);
  }

  getEventsTimeline(hours: number = 24): Observable<any> {
    return this.http.get(`${this.baseUrl}/statistics/events/timeline`, {
      params: { hours: hours.toString() }
    });
  }

  getNetworkHealthScore(): Observable<NetworkHealthScore> {
    return this.http.get<NetworkHealthScore>(`${this.baseUrl}/statistics/network-health-score`);
  }

  getTrafficSummary(): Observable<any> {
    return this.http.get(`${this.baseUrl}/statistics/traffic-summary`);
  }

  // ==================== VALIDATION ENDPOINTS ====================

  validateIP(ip: string): Observable<ValidationResult> {
    return this.http.post<ValidationResult>(`${this.baseUrl}/validation/ip`, { ip });
  }

  validateMAC(mac: string): Observable<ValidationResult> {
    return this.http.post<ValidationResult>(`${this.baseUrl}/validation/mac`, { mac });
  }

  validateIPRange(ipRange: string): Observable<ValidationResult> {
    return this.http.post<ValidationResult>(`${this.baseUrl}/validation/ip-range`, { ip_range: ipRange });
  }

  validateHostname(hostname: string): Observable<ValidationResult> {
    return this.http.post<ValidationResult>(`${this.baseUrl}/validation/hostname`, { hostname });
  }

  validateDevice(deviceData: any): Observable<{ valid: boolean; errors: any }> {
    return this.http.post<{ valid: boolean; errors: any }>(`${this.baseUrl}/validation/device`, deviceData);
  }

  checkIPInSubnet(ip: string, subnet: string): Observable<any> {
    return this.http.get(`${this.baseUrl}/validation/check-ip-in-subnet`, {
      params: { ip, subnet }
    });
  }
}