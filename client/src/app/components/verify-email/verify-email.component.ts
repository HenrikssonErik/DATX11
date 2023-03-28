import {
  HttpClient,
  HttpHeaders,
  HttpParams,
  HttpResponse,
} from '@angular/common/http';
import { Component, OnInit } from '@angular/core';
import { ActivatedRoute, Params } from '@angular/router';
import { resolve } from 'dns';
import { API_URL } from 'src/environments/environment';

@Component({
  selector: 'app-verify-email',
  templateUrl: './verify-email.component.html',
  styleUrls: ['./verify-email.component.scss'],
})
export class VerifyEmailComponent implements OnInit {
  verificationFinished!: Promise<Boolean>;
  responseMessage: string | undefined;
  errorCaught!: Promise<Boolean>;
  imgPath: string = 'emailVerification';

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
          this.responseMessage = response['cid'];

          setTimeout(() => {
            this.verificationFinished = Promise.resolve(true);
            this.imgPath = 'successVerification';
          }, 2000);

          // this.verificationFinished = new Promise((resolve) => {
          //   setTimeout(() => resolve(true), 2000);
          // }).then(() => (this.imgPath = 'successVerification'));
        },
        error: (error) => {
          let errorStatus = error.error.status;
          if (errorStatus == 'invalid_verification_token') {
            this.responseMessage =
              'The token is invalid. Sign up again to receive a new verification email';
          } else if (errorStatus === 'expired_verification_signature') {
            this.responseMessage =
              'The signature that expired. Sign up again to receive a new verification email!';
          }
          // this.responseMessage = error.error.status;
          console.log(this.responseMessage);

          setTimeout(() => {
            this.errorCaught = Promise.resolve(true);
            this.imgPath = 'errorVerification';
          }, 2000);

          // this.errorCaught = new Promise((resolve) => {
          //   setTimeout(() => resolve(true), 2000);
          // }).then(() => (this.imgPath = 'errorVerification'));

          console.log(error);
        },
      });
  }
}
