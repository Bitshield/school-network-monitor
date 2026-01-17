import { Component } from '@angular/core';

export interface NetworkStats {
  totalDevices: number;
  upDevices: number;
  downDevices: number;
}

@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.scss'],
})
export class AppComponent {
  connectionStatus = 'connected'; // for now assume ok

  stats: NetworkStats = {
    totalDevices: 0,
    upDevices: 0,
    downDevices: 0,
  };

  onStatsChanged(stats: NetworkStats) {
    this.stats = stats;
  }
}
