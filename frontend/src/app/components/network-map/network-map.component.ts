import { Component, OnInit, OnDestroy, ViewChild, ElementRef, Output, EventEmitter } from '@angular/core';
import { Subject } from 'rxjs';
import { takeUntil } from 'rxjs/operators';
import cytoscape, { Core, NodeSingular, EdgeSingular } from 'cytoscape';
import { ApiService, Device, Link, NetworkHealthScore } from '../../services/api.service';
import { WebsocketService, TopologyUpdate, DeviceStatusUpdate, LinkStatusUpdate } from '../../services/websocket.service';
import { NotificationService } from '../../services/notification.service';

interface NetworkStats {
  totalDevices: number;
  upDevices: number;
  downDevices: number;
  totalLinks: number;
  upLinks: number;
}

@Component({
  selector: 'app-network-map',
  templateUrl: './network-map.component.html',
  styleUrls: ['./network-map.component.scss']
})
export class NetworkMapComponent implements OnInit, OnDestroy {
  @ViewChild('cytoscapeContainer', { static: true }) cytoscapeContainer!: ElementRef;
  @Output() statsChanged = new EventEmitter<NetworkStats>();

  private cy!: Core;
  private destroy$ = new Subject<void>();
  
  devices: Device[] = [];
  links: Link[] = [];
  stats: NetworkStats = {
    totalDevices: 0,
    upDevices: 0,
    downDevices: 0,
    totalLinks: 0,
    upLinks: 0
  };

  selectedNode: any = null;
  isLoading = false;
  layoutType: 'grid' | 'circle' | 'breadthfirst' | 'cose' = 'breadthfirst';

  constructor(
    private api: ApiService,
    private ws: WebsocketService,
    private notifications: NotificationService
  ) {}

  ngOnInit(): void {
    this.initializeCytoscape();
    this.loadTopology();
    this.subscribeToUpdates();
  }

  ngOnDestroy(): void {
    this.destroy$.next();
    this.destroy$.complete();
    if (this.cy) {
      this.cy.destroy();
    }
  }

  // ==================== CYTOSCAPE INITIALIZATION ====================

  private initializeCytoscape(): void {
    this.cy = cytoscape({
      container: this.cytoscapeContainer.nativeElement,
      
      style: [
        // Node styles
        {
          selector: 'node',
          style: {
            'background-color': '#3b82f6',
            'label': 'data(label)',
            'color': '#1f2937',
            'font-size': '12px',
            'text-valign': 'bottom',
            'text-halign': 'center',
            'text-margin-y': 5,
            'width': 40,
            'height': 40,
            'border-width': 2,
            'border-color': '#1f2937'
          }
        },
        
        // Router nodes
        {
          selector: 'node[type="router"]',
          style: {
            'background-color': '#f97316',
            'shape': 'diamond'
          }
        },
        
        // Switch nodes
        {
          selector: 'node[type="switch"]',
          style: {
            'background-color': '#3b82f6',
            'shape': 'rectangle'
          }
        },
        
        // PC nodes
        {
          selector: 'node[type="pc"]',
          style: {
            'background-color': '#10b981',
            'shape': 'ellipse'
          }
        },
        
        // Server nodes
        {
          selector: 'node[type="server"]',
          style: {
            'background-color': '#8b5cf6',
            'shape': 'round-rectangle'
          }
        },
        
        // Printer nodes
        {
          selector: 'node[type="printer"]',
          style: {
            'background-color': '#f59e0b',
            'shape': 'triangle'
          }
        },
        
        // Access Point nodes
        {
          selector: 'node[type="access_point"]',
          style: {
            'background-color': '#06b6d4',
            'shape': 'star'
          }
        },
        
        // Status: UP
        {
          selector: 'node[status="UP"]',
          style: {
            'border-color': '#22c55e',
            'border-width': 3
          }
        },
        
        // Status: DOWN
       // Status: DOWN
// Status: DOWN
{
  selector: 'node[status="DOWN"]',
  style: {
    'border-color': '#ef4444',
    'border-width': 4
  }
},


        
        // Status: UNKNOWN
        {
          selector: 'node[status="UNKNOWN"]',
          style: {
            'border-color': '#6b7280',
            'border-style': 'dashed'
          }
        },
        
        // Selected node
        {
          selector: 'node:selected',
          style: {
            'overlay-color': '#3b82f6',
            'overlay-padding': 10,
            'overlay-opacity': 0.3
          }
        },
        
        // Edge (link) styles
        {
          selector: 'edge',
          style: {
            'width': 2,
            'line-color': '#94a3b8',
            'target-arrow-color': '#94a3b8',
            'target-arrow-shape': 'triangle',
            'curve-style': 'bezier'
          }
        },
        
        // Link status: UP
        {
          selector: 'edge[status="UP"]',
          style: {
            'line-color': '#22c55e',
            'target-arrow-color': '#22c55e',
            'width': 3
          }
        },
        
        // Link status: DOWN
        {
          selector: 'edge[status="DOWN"]',
          style: {
            'line-color': '#ef4444',
            'target-arrow-color': '#ef4444',
            'width': 4,
            'line-style': 'dashed'
          }
        },
        
        // Link status: DEGRADED
        {
          selector: 'edge[status="DEGRADED"]',
          style: {
            'line-color': '#f59e0b',
            'target-arrow-color': '#f59e0b',
            'width': 3
          }
        },
        
        // Selected edge
        {
          selector: 'edge:selected',
          style: {
            'overlay-color': '#3b82f6',
            'overlay-padding': 3,
            'overlay-opacity': 0.3
          }
        }
      ],
      
      layout: {
        name: 'breadthfirst',
        directed: true,
        padding: 10
      },
      
      minZoom: 0.3,
      maxZoom: 3,
      wheelSensitivity: 0.2
    });

    // Add event listeners
    this.cy.on('tap', 'node', (event) => {
      const node = event.target;
      this.onNodeClick(node);
    });

    this.cy.on('tap', 'edge', (event) => {
      const edge = event.target;
      this.onEdgeClick(edge);
    });

    this.cy.on('tap', (event) => {
      if (event.target === this.cy) {
        this.selectedNode = null;
      }
    });
  }

  // ==================== DATA LOADING ====================

  private loadTopology(): void {
    this.isLoading = true;
    
    // Load devices
    this.api.getDevices({ page_size: 1000 }).subscribe({
      next: (devices) => {
        this.devices = devices;
        this.addDevicesToGraph(devices);
        
        // Load links after devices are loaded
        this.loadLinks();
      },
      error: (error) => {
        console.error('Error loading devices:', error);
        this.notifications.error('Failed to load devices');
        this.isLoading = false;
      }
    });
  }

  private loadLinks(): void {
    this.api.getLinks({ page_size: 1000 }).subscribe({
      next: (links) => {
        this.links = links;
        this.addLinksToGraph(links);
        this.updateStats();
        this.applyLayout();
        this.isLoading = false;
      },
      error: (error) => {
        console.error('Error loading links:', error);
        this.notifications.error('Failed to load links');
        this.isLoading = false;
      }
    });
  }

  // ==================== GRAPH MANIPULATION ====================

private addDevicesToGraph(devices: Device[]): void {
  devices.forEach(device => {
    const classes = device.status === 'DOWN' ? 'status-down-node' : '';

    if (!this.cy.$id(device.id).length) {
      this.cy.add({
        group: 'nodes',
        data: {
          id: device.id,
          label: device.name,
          type: device.device_type,
          status: device.status,
          ip: device.ip,
          deviceData: device
        },
        classes // <== here (typed on ElementDefinition, not style)
      });
    } else {
      const node = this.cy.$id(device.id);
      node.data('status', device.status);
      node.data('deviceData', device);
      node.classes(classes);
    }
  });
}


  private addLinksToGraph(links: Link[]): void {
    links.forEach(link => {
      const edgeId = `edge-${link.id}`;
      
      if (!this.cy.$id(edgeId).length) {
        this.cy.add({
          group: 'edges',
          data: {
            id: edgeId,
            source: link.source_device_id,
            target: link.target_device_id,
            status: link.status,
            linkData: link
          }
        });
      } else {
        // Update existing edge
        const edge = this.cy.$id(edgeId);
        edge.data('status', link.status);
        edge.data('linkData', link);
      }
    });
  }

  private updateDeviceStatus(deviceId: string, status: string): void {
    const node = this.cy.$id(deviceId);
    if (node.length) {
      node.data('status', status);
      
      // Update in devices array
      const device = this.devices.find(d => d.id === deviceId);
      if (device) {
        device.status = status as any;
      }
      
      this.updateStats();
    }
  }

  private updateLinkStatus(linkId: string, status: string): void {
    const edgeId = `edge-${linkId}`;
    const edge = this.cy.$id(edgeId);
    
    if (edge.length) {
      edge.data('status', status);
      
      // Update in links array
      const link = this.links.find(l => l.id === linkId);
      if (link) {
        link.status = status as any;
      }
      
      this.updateStats();
    }
  }

  // ==================== WEBSOCKET UPDATES ====================

  private subscribeToUpdates(): void {
    // Topology updates
    this.ws.getTopologyUpdates()
      .pipe(takeUntil(this.destroy$))
      .subscribe((topology: TopologyUpdate) => {
        console.log('Topology update received:', topology);
        this.handleTopologyUpdate(topology);
      });

    // Device status updates
    this.ws.getDeviceStatusUpdates()
      .pipe(takeUntil(this.destroy$))
      .subscribe((update: DeviceStatusUpdate) => {
        console.log('Device status update:', update);
        this.updateDeviceStatus(update.device_id, update.status);
      });

    // Link status updates
    this.ws.getLinkStatusUpdates()
      .pipe(takeUntil(this.destroy$))
      .subscribe((update: LinkStatusUpdate) => {
        console.log('Link status update:', update);
        this.updateLinkStatus(update.link_id, update.status);
      });
  }

  private handleTopologyUpdate(topology: TopologyUpdate): void {
    // Clear existing graph
    this.cy.elements().remove();
    
    // Add updated devices and links
    if (topology.devices) {
      this.devices = topology.devices;
      this.addDevicesToGraph(topology.devices);
    }
    
    if (topology.links) {
      this.links = topology.links;
      this.addLinksToGraph(topology.links);
    }
    
    this.updateStats();
    this.applyLayout();
  }

  // ==================== STATISTICS ====================

  private updateStats(): void {
    this.stats = {
      totalDevices: this.devices.length,
      upDevices: this.devices.filter(d => d.status === 'UP').length,
      downDevices: this.devices.filter(d => d.status === 'DOWN').length,
      totalLinks: this.links.length,
      upLinks: this.links.filter(l => l.status === 'UP').length
    };
    
    this.statsChanged.emit(this.stats);
  }

  // ==================== LAYOUT ====================

  applyLayout(layoutName?: 'grid' | 'circle' | 'breadthfirst' | 'cose'): void {
    if (layoutName) {
      this.layoutType = layoutName;
    }

    const layoutOptions: any = {
      name: this.layoutType,
      animate: true,
      animationDuration: 500,
      padding: 30
    };

    if (this.layoutType === 'breadthfirst') {
      layoutOptions.directed = true;
      layoutOptions.spacingFactor = 1.5;
    } else if (this.layoutType === 'cose') {
      layoutOptions.nodeRepulsion = 8000;
      layoutOptions.idealEdgeLength = 100;
    }

    this.cy.layout(layoutOptions).run();
  }

  // ==================== USER INTERACTIONS ====================

  private onNodeClick(node: NodeSingular): void {
    const deviceData = node.data('deviceData');
    this.selectedNode = {
      type: 'device',
      data: deviceData,
      id: deviceData.id,
      name: deviceData.name,
      status: deviceData.status,
      ip: deviceData.ip,
      deviceType: deviceData.device_type
    };
  }

  private onEdgeClick(edge: EdgeSingular): void {
    const linkData = edge.data('linkData');
    this.selectedNode = {
      type: 'link',
      data: linkData,
      id: linkData.id,
      status: linkData.status,
      sourceId: linkData.source_device_id,
      targetId: linkData.target_device_id
    };
  }

  centerGraph(): void {
    this.cy.fit(undefined, 50);
  }

  resetZoom(): void {
    this.cy.zoom(1);
    this.cy.center();
  }

  zoomIn(): void {
    this.cy.zoom(this.cy.zoom() * 1.2);
  }

  zoomOut(): void {
    this.cy.zoom(this.cy.zoom() * 0.8);
  }

  // ==================== ACTIONS ====================

  refresh(): void {
    this.loadTopology();
    this.notifications.info('Refreshing topology...');
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

  testLink(linkId: string): void {
    this.api.testLink(linkId).subscribe({
      next: (result) => {
        this.notifications.success('Link test completed');
      },
      error: (error) => {
        this.notifications.showApiError(error);
      }
    });
  }
}