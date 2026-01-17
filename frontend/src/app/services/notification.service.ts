import { Injectable } from '@angular/core';
import { Subject, Observable } from 'rxjs';

export type NotificationType = 'success' | 'error' | 'warning' | 'info';

export interface Notification {
  id: string;
  type: NotificationType;
  title?: string;
  message: string;
  duration?: number;
  action?: {
    label: string;
    callback: () => void;
  };
}

@Injectable({
  providedIn: 'root'
})
export class NotificationService {
  private notificationSubject = new Subject<Notification>();
  public notifications$: Observable<Notification> = this.notificationSubject.asObservable();

  private idCounter = 0;

  constructor() {}

  /**
   * Show a success notification
   */
  success(message: string, title?: string, duration: number = 3000): void {
    this.show('success', message, title, duration);
  }

  /**
   * Show an error notification
   */
  error(message: string, title?: string, duration: number = 5000): void {
    this.show('error', message, title, duration);
  }

  /**
   * Show a warning notification
   */
  warning(message: string, title?: string, duration: number = 4000): void {
    this.show('warning', message, title, duration);
  }

  /**
   * Show an info notification
   */
  info(message: string, title?: string, duration: number = 3000): void {
    this.show('info', message, title, duration);
  }

  /**
   * Show a notification with custom configuration
   */
  showCustom(config: Partial<Notification>): void {
    const notification: Notification = {
      id: `notification-${this.idCounter++}`,
      type: config.type || 'info',
      title: config.title,
      message: config.message || '',
      duration: config.duration || 3000,
      action: config.action
    };

    this.notificationSubject.next(notification);
  }

  /**
   * Show a notification
   */
  private show(type: NotificationType, message: string, title?: string, duration?: number): void {
    const notification: Notification = {
      id: `notification-${this.idCounter++}`,
      type,
      title,
      message,
      duration
    };

    this.notificationSubject.next(notification);
  }

  /**
   * Show notification from API error
   */
  showApiError(error: any): void {
    let message = 'An error occurred';
    
    if (error?.error?.detail) {
      if (typeof error.error.detail === 'string') {
        message = error.error.detail;
      } else if (Array.isArray(error.error.detail)) {
        message = error.error.detail.map((d: any) => d.msg || d).join(', ');
      }
    } else if (error?.message) {
      message = error.message;
    } else if (typeof error === 'string') {
      message = error;
    }

    this.error(message, 'Error');
  }
}