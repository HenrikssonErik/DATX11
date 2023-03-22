import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { API_URL } from 'src/environments/environment';

@Injectable({
  providedIn: 'root',
})
export class CourseService {
  constructor(private http: HttpClient) {}

  getCourses(): Observable<any> {
    let headers: HttpHeaders = new HttpHeaders();
    headers = headers.append('Cookies', document.cookie);
    return this.http.get(`${API_URL}/getCourses`, { headers });
  }
}
