import {
  HttpClient,
  HttpHeaders,
  HttpParams,
  HttpResponse,
} from '@angular/common/http';
import { Component, OnInit } from '@angular/core';
import { ActivatedRoute, Params } from '@angular/router';
import { API_URL } from 'src/environments/environment';

@Component({
  selector: 'app-verify-email',
  templateUrl: './verify-email.component.html',
  styleUrls: ['./verify-email.component.scss'],
})
export class VerifyEmailComponent implements OnInit {
  cid$: string | undefined;

  constructor(
    private http: HttpClient,
    private activatedRoute: ActivatedRoute
  ) {}

  ngOnInit(): void {
    this.activatedRoute.params.subscribe((params) => {
      this.verifyEmail(params);
    });
  }

  verifyEmail(params: Params): void {
    /*     let header: HttpHeaders = new HttpHeaders();

    header.append('Content-Type', 'application/json'); */

    this.http
      .post<HttpResponse<any>>(`${API_URL}/verify_email`, params)
      .subscribe({
        next: (response: any) => {
          this.cid$ = response['cid'];
          console.log(response);
        },
        error: (error) => {
          console.log(error);
        },
      });
  }
}
