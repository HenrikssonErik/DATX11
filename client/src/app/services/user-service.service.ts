import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Observable, map } from 'rxjs';
import { API_URL } from 'src/environments/environment';
import { User, Users } from '../models/user';

@Injectable({
  providedIn: 'root',
})
export class UserService {
  constructor(private http: HttpClient) {}

  getUserData(): Observable<any> {
    let headers: HttpHeaders = new HttpHeaders();
    headers = headers
      .append('Cookies', document.cookie)
      .set('Cache-Control', 'public, max-age=3600');
    return this.http.get<User>(`${API_URL}/getUserInfo`, { headers });
  }

  getUsersInCourse(course: number): Observable<User[]> {
    let headers: HttpHeaders = new HttpHeaders();
    headers = headers
      .append('Cookies', document.cookie)
      .set('Cache-Control', 'public, max-age=3600');
    return this.http
      .get<Users>(`${API_URL}/getUsersInCourse?Course=${course}`, {
        headers,
      })
      .pipe(map((res) => res.Users));
  }
}
