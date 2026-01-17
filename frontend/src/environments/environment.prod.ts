export const environment = {
  production: true,
  apiUrl: 'https://your-production-domain.com/api/v1',
  wsUrl: 'wss://your-production-domain.com/ws',
  appName: 'School Network Monitor',
  appVersion: '1.0.0',
  
  // Feature flags
  features: {
    deviceDiscovery: true,
    linkDiscovery: true,
    realTimeMonitoring: true,
    cableHealth: true,
    snmp: true,
    events: true,
    statistics: true,
    validation: true,
    portManagement: true
  },
  
  // Monitoring settings
  monitoring: {
    defaultInterval: 60000, // 60 seconds
    timeout: 5000, // 5 seconds
    retryAttempts: 3
  },
  
  // WebSocket settings
  websocket: {
    reconnectInterval: 5000, // 5 seconds
    maxReconnectAttempts: 10,
    heartbeatInterval: 30000 // 30 seconds
  },
  
  // UI settings
  ui: {
    toastDuration: 3000,
    defaultPageSize: 20,
    maxPageSize: 100,
    refreshInterval: 30000, // 30 seconds
    chartRefreshInterval: 10000 // 10 seconds
  },
  
  // Network discovery
  discovery: {
    defaultNetworkRange: '192.168.1.0/24',
    timeout: 2000,
    maxConcurrent: 50
  },
  
  // SNMP settings
  snmp: {
    defaultCommunity: 'public',
    timeout: 5000,
    retries: 2
  },
  
  // Pagination
  pagination: {
    defaultPageSize: 20,
    pageSizeOptions: [10, 20, 50, 100]
  },
  
  // Chart colors
  chartColors: {
    devices: {
      router: '#f97316', // orange
      switch: '#3b82f6', // blue
      pc: '#10b981', // green
      server: '#8b5cf6', // purple
      printer: '#f59e0b', // amber
      access_point: '#06b6d4' // cyan
    },
    status: {
      up: '#22c55e', // green
      down: '#ef4444', // red
      degraded: '#f59e0b', // amber
      unknown: '#6b7280' // gray
    },
    severity: {
      critical: '#dc2626', // red
      warning: '#f59e0b', // amber
      info: '#3b82f6' // blue
    }
  }
};