import { HttpClient, HttpResponse } from '@angular/common/http';
import { Component, OnInit } from '@angular/core';
import { ActivatedRoute, Params, Router } from '@angular/router';
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
    private activatedRoute: ActivatedRoute,
    private router: Router
  ) {}

  ngOnInit(): void {
    this.activatedRoute.params.subscribe((params) => {
      this.verifyEmail(params);
    });
  }

  verifyEmail(params: Params): void {
    this.http
      .post<HttpResponse<any>>(`${API_URL}/verify_email`, params)
      .subscribe({
        next: (response: any) => {
          this.responseMessage = response['cid'];

          setTimeout(() => {
            this.verificationFinished = Promise.resolve(true);
            this.imgPath = 'successVerification';
          }, 1500);
        },
        error: (error) => {
          this.responseMessage = error.error.status;
          console.log(this.responseMessage);

          setTimeout(() => {
            this.errorCaught = Promise.resolve(true);
            this.imgPath = 'errorVerification';
          }, 1500);
          console.log(error);
        },
        complete: () => {
          setTimeout(() => {
            this.router.navigate(['/login']);
          }, 5000);
        },
      });
  }
}
