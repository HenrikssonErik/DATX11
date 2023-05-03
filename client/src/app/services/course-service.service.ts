import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { map, mergeMap, Observable, switchMap } from 'rxjs';
import { API_URL } from 'src/environments/environment';
import { Courses, ProgressItem } from '../models/courses';
import { Course } from '../models/courses';

@Injectable({
  providedIn: 'root',
})
export class CourseService {
  constructor(private http: HttpClient) {}

  getCourses(): Observable<Course[]> {
    const headers = new HttpHeaders()
      .append('Cookies', document.cookie)
      .set('Cache-Control', 'public, max-age=3600');
    return this.http
      .get<Courses>(`${API_URL}/getCourses`, { headers })
      .pipe(map((res) => res.courses));
  }

  getCourse(id: number): Observable<Course> {
    const headers = new HttpHeaders()
      .append('Cookies', document.cookie)
      .set('Cache-Control', 'public, max-age=3600');
    return this.http.get<Course>(`${API_URL}/getCourse?Course=${id}`, {
      headers,
    });
  }

  getCourseProgress(): Observable<ProgressItem[]> {
    const headers = new HttpHeaders()
      .append('Cookies', document.cookie)
      .set('Cache-Control', 'public, max-age=3600');
    return this.http.get<ProgressItem[]>(`${API_URL}/getCourseProgress`, {
      headers,
    });
  }

  changeCourseName(newName: string, courseId: number): Observable<any> {
    const headers = new HttpHeaders().append('Cookies', document.cookie);
    return this.http.post<Course>(
      `${API_URL}/changeCourseName`,
      { Name: newName, Course: courseId },
      {
        observe: 'response',
        headers: headers,
      }
    );
  }

  createAssignment(
    assignmentNr: string,
    description: string,
    courseId: number,
    deadline: Date
  ): Observable<any> {
    const headers = new HttpHeaders().append('Cookies', document.cookie);
    return this.http.post<any>(
      `${API_URL}/createAssignment`,
      {
        AssignmentNr: assignmentNr,
        Description: description,
        Course: courseId,
        Date: deadline,
      },
      {
        observe: 'response',
        headers: headers,
      }
    );
  }
}
