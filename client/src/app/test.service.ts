import { Injectable } from '@angular/core';
import { HttpClient, HttpErrorResponse } from '@angular/common/http';
import { Observable } from 'rxjs';
import { throwError } from 'rxjs';
import { API_URL } from 'src/environments/environment';

@Injectable()
export class TestApiService {
  constructor(private http: HttpClient) {}

  testGET(): Observable<any> {
    return this.http.get(`${API_URL}/test`);
  }
}
