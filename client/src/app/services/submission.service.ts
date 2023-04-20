import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { API_URL } from 'src/environments/environment';

@Injectable({
  providedIn: 'root',
})
export class SubmissionService {
  constructor(private http: HttpClient) {}

  getSubmission(courseId: number, assignmentNr: number): Observable<any> {
    const headers = new HttpHeaders()
      .append('Cookies', document.cookie)
      .set('Cache-Control', 'public, max-age=3600');

    return this.http.get<any>(
      `${API_URL}/getFeedback?Course=${courseId}&Assignment=${assignmentNr}`,
      { headers }
    );
  }

  /* getAssignmentOverView(courseId: number): Observable<any> {
  } */
}
