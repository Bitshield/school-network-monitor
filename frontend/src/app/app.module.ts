import { NgModule } from '@angular/core';
import { BrowserModule } from '@angular/platform-browser';
import { BrowserAnimationsModule } from '@angular/platform-browser/animations';
import { HttpClientModule, HTTP_INTERCEPTORS } from '@angular/common/http';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';
import { RouterModule } from '@angular/router';

import { AppComponent } from './app.component';

// Services
import { ApiService } from './services/api.service';
import { WebsocketService } from './services/websocket.service';
import { NotificationService } from './services/notification.service';

// Routing
import { AppRoutingModule } from '../routing.module';

// Interceptors
import { ErrorInterceptor } from './interceptor/error.interceptor';

// Components
import { NetworkMapComponent } from './components/network-map/network-map.component';
import { DashboardComponent } from './components/dashboard/dashboard.component';
import { DevicesComponent } from './components/devices/devices.component';
import { LinksComponent } from './components/links/links.component';
import { EventsComponent } from './components/events/events.component';
import { PortsComponent } from './components/ports/ports.component';
import { DiscoveryComponent } from './components/discovery/discovery.component';
import { AuthInterceptor } from './interceptor/auh.interceptor';

@NgModule({
  declarations: [
    AppComponent,
    NetworkMapComponent,
    DashboardComponent,
    DevicesComponent,
    LinksComponent,
    EventsComponent,
    PortsComponent,
    DiscoveryComponent,
  ],
  imports: [
    BrowserModule,
    BrowserAnimationsModule,
    HttpClientModule,
    FormsModule,
    ReactiveFormsModule,
    RouterModule,          // Needed for routerLink
    AppRoutingModule
  ],
  providers: [
    ApiService,
    WebsocketService,
    NotificationService,
    {
      provide: HTTP_INTERCEPTORS,
      useClass: ErrorInterceptor,
      multi: true
    },
    {
      provide: HTTP_INTERCEPTORS,
      useClass: AuthInterceptor,
      multi: true
    }
  ],
  bootstrap: [AppComponent]
})
export class AppModule { }
