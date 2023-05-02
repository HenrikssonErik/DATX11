import { HttpClient, HttpResponse } from '@angular/common/http';
import { Component, OnInit } from '@angular/core';
import {
  UntypedFormBuilder,
  UntypedFormGroup,
  Validators,
} from '@angular/forms';
import { ActivatedRoute, Params } from '@angular/router';
import { API_URL } from 'src/environments/environment';

@Component({
  selector: 'app-forgot-pwd',
  templateUrl: './forgot-pwd.component.html',
  styleUrls: ['./forgot-pwd.component.scss'],
})
export class ForgotPwdComponent implements OnInit {
  passwordForm: UntypedFormGroup = new UntypedFormGroup({});

  tokenValid!: Promise<Boolean>;

  constructor(
    private fb: UntypedFormBuilder,
    private http: HttpClient,
    private activatedRoute: ActivatedRoute
  ) {}

  ngOnInit(): void {
    this.activatedRoute.params.subscribe((params) => {
      this.verifyToken(params);
    });
  }

  initializePwdForm(cid: string): void {
    this.passwordForm = this.fb.group({
      cid: this.fb.control({ value: cid, disabled: true }),
      password: ['', Validators.required],
      verifyPassword: ['', Validators.required, Validators],
    });
  }

  verifyToken(params: Params): void {
    this.http
      .post<HttpResponse<any>>(`${API_URL}/verify_email`, params)
      .subscribe({
        next: (response: any) => {
          const cid: string = response['cid'];
          this.tokenValid = Promise.resolve(true);
          this.initializePwdForm(cid);
          console.log(cid);
        },
        error: (error) => {
          console.log(error);
          this.tokenValid = Promise.resolve(false);
        },
        complete: () => {},
      });
  }
}
