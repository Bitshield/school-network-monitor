import { Injectable } from '@angular/core';
import { Router, CanActivate, ActivatedRouteSnapshot, RouterStateSnapshot } from '@angular/router';
import { ApiService } from '../services/api.service';

@Injectable({
  providedIn: 'root'
})
export class AuthGuard implements CanActivate {
  constructor(
    private router: Router,
    private apiService: ApiService
  ) {}

  canActivate(route: ActivatedRouteSnapshot, state: RouterStateSnapshot): boolean {
    const currentUser = this.apiService.currentUserValue;
    
    if (currentUser) {
      // Check if route requires specific role
      if (route.data['roles'] && !route.data['roles'].includes(currentUser.role)) {
        // Role not authorized, redirect to home
        this.router.navigate(['/']);
        return false;
      }
      
      // Authorized
      return true;
    }

    // Not logged in, redirect to login page with return url
    this.router.navigate(['/login'], { queryParams: { returnUrl: state.url } });
    return false;
  }
}