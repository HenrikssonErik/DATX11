import { HttpClient, HttpHeaders, HttpResponse } from '@angular/common/http';
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

  getTestingFeedback(
    courseId: number,
    assignmentNr: number,
    groupId: number
  ): Observable<any> {
    const headers = new HttpHeaders()
      .append('Cookies', document.cookie)
      .set('Cache-Control', 'public, max-age=3600');

    return this.http.get<any>(
      `${API_URL}/getTestingFeedback?Course=${courseId}&Assignment=${assignmentNr}&Group=${groupId}`,
      { headers }
    );
  }

  getAssignmentOverView(courseId: number): Observable<any> {
    const headers = new HttpHeaders()
      .append('Cookies', document.cookie)
      .set('Cache-Control', 'public, max-age=3600');

    return this.http.get<any>(
      `${API_URL}/assignmentsOverview?Course=${courseId}`,
      { headers }
    );
  }

  setFeedback(
    course: number,
    assignmentNr: number,
    submission: number,
    feedback: string,
    grade: boolean,
    groupId: number
  ): Observable<any> {
    const headers = new HttpHeaders().append('Cookies', document.cookie);

    return this.http.post<HttpResponse<any>>(
      `${API_URL}/setFeedback`,
      {
        Course: course,
        Assignment: assignmentNr,
        Submission: submission,
        Feedback: feedback,
        Grade: grade,
        Group: groupId,
      },
      {
        observe: 'response',
        headers: headers,
      }
    );
  }

  getFileNames(courseId: number, assignmentNr: number): Observable<any> {
    const headers = new HttpHeaders()
      .append('Cookies', document.cookie)
      .set('Cache-Control', 'public, max-age=3600');

    return this.http.get<any>(
      `${API_URL}/getFilenames?Course=${courseId}&Assignment=${assignmentNr}`,
      { headers }
    );
  }

  downloadSubmissionFile(
    courseId: number,
    groupId: number,
    assignmentNr: number,
    submissionId: number,
    filename: string
  ): void {
    const headers = new HttpHeaders().append('Cookies', document.cookie);

    this.http
      .get(
        `${API_URL}/getAssignmentFile?course=${courseId}&groupId=${groupId}&assignment=${assignmentNr}&submission=${submissionId}&filename=${filename}`,
        { headers, responseType: 'blob' }
      )
      .subscribe((response) => {
        const blob = new Blob([response], { type: response.type });
        const objectUrl = URL.createObjectURL(blob);
        const anchor = document.createElement('a');
        anchor.href = objectUrl;
        anchor.download = filename;
        document.body.appendChild(anchor);
        anchor.click();
        document.body.removeChild(anchor);
      });
  }
}
