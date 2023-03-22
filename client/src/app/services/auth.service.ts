import { Injectable } from '@angular/core';

@Injectable({
  providedIn: 'root',
})
export class AuthService {
  constructor() {}

  isLoggedIn() {
    if (document.cookie.includes('Token')) {
      return true;
    } else {
      return false;
    }
  }
}
