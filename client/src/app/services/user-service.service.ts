import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { API_URL } from 'src/environments/environment';
import { User } from '../models/user';

@Injectable({
  providedIn: 'root',
})
export class UserService {
  constructor(private http: HttpClient) {}

  getUserData(): Observable<any> {
    let headers: HttpHeaders = new HttpHeaders();
    headers = headers.append('Cookies', document.cookie);
    return this.http.get<User>(`${API_URL}/getUserInfo`, { headers });
  }
}
