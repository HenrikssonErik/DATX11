import { HttpClient, HttpResponse } from '@angular/common/http';
import { Component, OnInit } from '@angular/core';
import {
  UntypedFormBuilder,
  UntypedFormGroup,
  Validators,
} from '@angular/forms';
import { ActivatedRoute, Params } from '@angular/router';
import { ToastrService } from 'ngx-toastr';
import { ToastrResponseService } from 'src/app/services/toastr-response.service';
import { API_URL } from 'src/environments/environment';

@Component({
  selector: 'app-forgot-pwd',
  templateUrl: './forgot-pwd.component.html',
  styleUrls: ['./forgot-pwd.component.scss'],
})
export class ForgotPwdComponent implements OnInit {
  passwordForm: UntypedFormGroup = new UntypedFormGroup({});
  imgSrc: string = 'pwd_success';
  token!: Params;

  tokenValid!: Promise<Boolean>;

  constructor(
    private fb: UntypedFormBuilder,
    private http: HttpClient,
    private activatedRoute: ActivatedRoute,
    private toastr: ToastrService,
    private toastrResponse: ToastrResponseService
  ) {}

  ngOnInit(): void {
    this.activatedRoute.params.subscribe((params) => {
      this.token = params;
      this.verifyToken(params);
    });
  }

  initializePwdForm(cid: string): void {
    this.passwordForm = this.fb.group({
      cid: this.fb.control({ value: cid, disabled: true }),
      password: ['', Validators.required],
      verifyPassword: ['', Validators.required],
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
          this.imgSrc = 'pwd_success';
          console.log(cid);
        },
        error: (error) => {
          console.log(error);
          this.imgSrc = 'pwd_error';
          this.tokenValid = Promise.resolve(false);
        },
        complete: () => {},
      });
  }

  onInputFocus(input: string, form: UntypedFormGroup): void {
    const control = form.get(input);

    if (control) {
      const isValid = control.valid;
      const isInvalid = control.invalid && (control.dirty || control.touched);
      const el = document.getElementById(input);

      el?.classList.toggle('success', isValid);
      el?.classList.toggle('error', isInvalid);
      el?.classList.toggle('success', !isInvalid && !isValid);
    }
  }

  onNewPassword(): void {
    if (this.passwordForm.invalid) {
      return;
    }

    const passForm = new FormData();
    const cid = this.passwordForm.get('cid');
    const pass = this.passwordForm.get('password');
    const verificationPass = this.passwordForm.get('verifyPassword');

    if (!cid || !pass || !verificationPass) {
      return;
    }

    if (pass != verificationPass) {
      this.toastr.error(
        'Make sure the passwords are the same.',
        'Nonidentical passwords!'
      );
      return;
    }

    passForm.append('cid', cid.value);
    passForm.append('password', pass.value);
    passForm.append('verificationPassword', verificationPass.value);

    this.http
      .post<HttpResponse<any>>(
        `${API_URL}/new_pwd`,
        { formData: passForm, token: this.token },
        {
          observe: 'response',
        }
      )
      .subscribe({
        next: (response: any) => {
          console.log(response);
        },
        error: (err) => {
          let statusMsg = err.error.status;
          const [errorMessage, errorTitle]: string[] =
            this.toastrResponse.getToastrResponse(statusMsg);
          this.toastr.error(errorMessage, errorTitle, {
            closeButton: true,
          });
        },
        complete: () => {
          this.toastr.success(undefined, 'Password changed!', {
            closeButton: true,
          });
        },
      });
  }
}
