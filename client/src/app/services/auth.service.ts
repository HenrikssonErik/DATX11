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

  logOut() {
    if (document.cookie.includes('Token')) {
      document.cookie = 'Token=; expires=Thu, 01 Jan 1970 00:00:00 UTC;';
      this.isAuthenticated$.next(false);
      location.reload();
    }
  }
}
