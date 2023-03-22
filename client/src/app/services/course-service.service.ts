import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { map, mergeMap, Observable, switchMap } from 'rxjs';
import { API_URL } from 'src/environments/environment';
import { Courses } from '../models/courses';
import { Course } from '../models/courses';

@Injectable({
  providedIn: 'root',
})
export class CourseService {
  constructor(private http: HttpClient) {}

  getCourses(): Observable<Course[]> {
    const headers = new HttpHeaders().append('Cookies', document.cookie);
    return this.http
      .get<Courses>(`${API_URL}/getCourses`, { headers })
      .pipe(map((res) => res.courses));
  }
}
