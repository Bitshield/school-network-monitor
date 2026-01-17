import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';

// Components will be imported in next parts
// import { DashboardComponent } from './components/dashboard/dashboard.component';
// import { DevicesComponent } from './components/devices/devices.component';
// import { DeviceDetailComponent } from './components/device-detail/device-detail.component';
// import { LinksComponent } from './components/links/links.component';
// import { LinkDetailComponent } from './components/link-detail/link-detail.component';
// import { PortsComponent } from './components/ports/ports.component';
// import { EventsComponent } from './components/events/events.component';
// import { CableHealthComponent } from './components/cable-health/cable-health.component';
// import { TopologyComponent } from './components/topology/topology.component';
// import { MonitoringComponent } from './components/monitoring/monitoring.component';
// import { DiscoveryComponent } from './components/discovery/discovery.component';
// import { StatisticsComponent } from './components/statistics/statistics.component';
// import { SettingsComponent } from './components/settings/settings.component';

const routes: Routes = [
  // Main routes - will be uncommented in next parts
  // { path: '', redirectTo: '/dashboard', pathMatch: 'full' },
  // { path: 'dashboard', component: DashboardComponent },
  // { path: 'devices', component: DevicesComponent },
  // { path: 'devices/:id', component: DeviceDetailComponent },
  // { path: 'links', component: LinksComponent },
  // { path: 'links/:id', component: LinkDetailComponent },
  // { path: 'ports', component: PortsComponent },
  // { path: 'events', component: EventsComponent },
  // { path: 'cable-health', component: CableHealthComponent },
  // { path: 'topology', component: TopologyComponent },
  // { path: 'monitoring', component: MonitoringComponent },
  // { path: 'discovery', component: DiscoveryComponent },
  // { path: 'statistics', component: StatisticsComponent },
  // { path: 'settings', component: SettingsComponent },
  
  // Fallback route
  { path: '**', redirectTo: '' }
];

@NgModule({
  imports: [RouterModule.forRoot(routes)],
  exports: [RouterModule]
})
export class AppRoutingModule { }