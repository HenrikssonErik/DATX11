import { HttpClient, HttpHeaders, HttpResponse } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { API_URL } from 'src/environments/environment';

@Injectable({
  providedIn: 'root',
})
export class GroupService {
  constructor(private http: HttpClient) {}

  getGroups(courseId: number): Observable<any> {
    const headers = new HttpHeaders()
      .append('Cookies', document.cookie)
      .set('Cache-Control', 'public, max-age=3600');

    return this.http.get<any>(`${API_URL}/getGroups?Course=${courseId}`, {
      headers,
    });
  }

  getMyGroup(courseId: number): Observable<any> {
    const headers = new HttpHeaders()
      .append('Cookies', document.cookie)
      .set('Cache-Control', 'public, max-age=3600');

    return this.http.get<any>(`${API_URL}/getMyGroup?Course=${courseId}`, {
      headers,
    });
  }

  removeFromGroup(
    courseId: number,
    groupId: number,
    user: number
  ): Observable<any> {
    const headers = new HttpHeaders()
      .append('Cookies', document.cookie)
      .set('Cache-Control', 'public, max-age=3600');

    return this.http.post<HttpResponse<any>>(
      `${API_URL}/removeFromGroup`,
      { User: user, Group: groupId, Course: courseId },
      {
        observe: 'response',
        headers: headers,
      }
    );
  }

  joinGroup(courseId: number, groupId: number, user: number): Observable<any> {
    const headers = new HttpHeaders().append('Cookies', document.cookie);

    return this.http.post<HttpResponse<any>>(
      `${API_URL}/addToGroup`,
      { User: user, Group: groupId, Course: courseId },
      {
        observe: 'response',
        headers: headers,
      }
    );
  }

  createGroup(courseId: number): Observable<any> {
    const headers = new HttpHeaders().append('Cookies', document.cookie);

    return this.http.post<HttpResponse<any>>(
      `${API_URL}/createGroup`,
      { Course: courseId },
      {
        observe: 'response',
        headers: headers,
      }
    );
  }

  getGroup(groupId: number, courseId: number) {
    const headers = new HttpHeaders()
      .append('Cookies', document.cookie)
      .set('Cache-Control', 'public, max-age=3600');

    return this.http.get<any>(
      `${API_URL}/getGroup?Course=${courseId}&GroupId=${groupId}`,
      {
        headers,
      }
    );
  }
}
