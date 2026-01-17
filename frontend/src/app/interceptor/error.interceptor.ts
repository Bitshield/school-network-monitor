import { Injectable } from '@angular/core';
import { HttpRequest, HttpHandler, HttpEvent, HttpInterceptor, HttpErrorResponse } from '@angular/common/http';
import { Observable, throwError } from 'rxjs';
import { catchError } from 'rxjs/operators';
import { NotificationService } from '../services/notification.service';

@Injectable()
export class ErrorInterceptor implements HttpInterceptor {
  constructor(private notificationService: NotificationService) {}

  intercept(request: HttpRequest<any>, next: HttpHandler): Observable<HttpEvent<any>> {
    return next.handle(request).pipe(
      catchError((error: HttpErrorResponse) => {
        let errorMessage = 'An unknown error occurred';
        
        if (error.error instanceof ErrorEvent) {
          // Client-side error
          errorMessage = `Error: ${error.error.message}`;
        } else {
          // Server-side error
          if (error.error?.detail) {
            if (typeof error.error.detail === 'string') {
              errorMessage = error.error.detail;
            } else if (Array.isArray(error.error.detail)) {
              errorMessage = error.error.detail.map((d: any) => d.msg || d.message || d).join(', ');
            } else if (typeof error.error.detail === 'object') {
              errorMessage = JSON.stringify(error.error.detail);
            }
          } else if (error.error?.message) {
            errorMessage = error.error.message;
          } else if (error.message) {
            errorMessage = error.message;
          } else {
            errorMessage = `Server Error: ${error.status} - ${error.statusText}`;
          }
        }

        // Log the error
        console.error('HTTP Error:', {
          status: error.status,
          message: errorMessage,
          url: request.url,
          error: error
        });

        // Show notification for specific error codes
        if (error.status >= 500) {
          this.notificationService.error(errorMessage, 'Server Error');
        } else if (error.status === 404) {
          this.notificationService.warning('Resource not found', 'Not Found');
        } else if (error.status === 403) {
          this.notificationService.warning('You don\'t have permission to perform this action', 'Forbidden');
        } else if (error.status === 409) {
          this.notificationService.warning(errorMessage, 'Conflict');
        } else if (error.status === 400) {
          this.notificationService.warning(errorMessage, 'Invalid Request');
        }

        return throwError(() => new Error(errorMessage));
      })
    );
  }
}