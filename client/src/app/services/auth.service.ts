import { Injectable } from '@angular/core';
import { BehaviorSubject, Observable } from 'rxjs';

@Injectable({
  providedIn: 'root',
})
export class AuthService {
  private isAuthenticated$: BehaviorSubject<boolean> =
    new BehaviorSubject<boolean>(false);

  constructor() {
    this.isLoggedIn();
  }

  get isAuthenticated(): Observable<boolean> {
    return this.isAuthenticated$.asObservable();
  }

  isLoggedIn() {
    if (document.cookie.includes('Token')) {
      this.isAuthenticated$.next(true);
      return true;
    } else {
      this.isAuthenticated$.next(false);
      return false;
    }
  }

  isAdminOrTeacher() {
    if (document.cookie.includes('Role')) {
      const roleCookie = document.cookie
        .split('; ')
        .find((row) => row.startsWith('Role'));
      const role = roleCookie ? roleCookie.split('=')[1] : null;
      if (role === 'Admin' || role === 'Teacher') {
        return true;
      } else {
        return false;
      }
    }
    return false;
  }

  async logOut() {
    if (document.cookie.includes('Token')) {
      console.log('inIf');
      document.cookie = 'Token=; expires=Thu, 01 Jan 1970 00:00:00 UTC;';
      this.isAuthenticated$.next(false);
      await this.delay(500);
      location.reload();
    }
  }

  delay(ms: number) {
    return new Promise((resolve) => setTimeout(resolve, ms));
  }
}
