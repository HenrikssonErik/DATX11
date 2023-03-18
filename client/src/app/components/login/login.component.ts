import { HttpClient, HttpResponse } from '@angular/common/http';
import { Component, OnInit } from '@angular/core';
import { FormBuilder, FormGroup, Validators } from '@angular/forms';
import { ToastrService } from 'ngx-toastr';
import { ToastrResponseService } from 'src/app/services/toastr-response.service';
import { TooltipEnablerService } from 'src/app/services/tooltip-enabler.service';
import { API_URL } from 'src/environments/environment';

@Component({
  selector: 'app-login',
  templateUrl: './login.component.html',

  styleUrls: ['./login.component.scss'],
})
export class LoginComponent implements OnInit {
  loginForm: FormGroup = new FormGroup({});
  signUpForm: FormGroup = new FormGroup({});
  submitFailed: boolean = false;
  success: boolean = false;
  signUpFailed: boolean = false;
  signUpSuccess: boolean = false;
  bcrypt = require('bcryptjs');
  cid: string = '';

  constructor(
    private fb: FormBuilder,
    private http: HttpClient,
    private toastr: ToastrService,
    private tooltipEnabler: TooltipEnablerService,
    private toastrResponse: ToastrResponseService
  ) {}

  ngOnInit(): void {
    this.loginForm = this.fb.group({
      email: ['', [Validators.required, Validators.email]],
      password: ['', [Validators.required]],
      rememberMe: [false],
    });

    this.signUpForm = this.fb.group({
      cid: ['', [Validators.required]],
      signUpemail: [''],
      signUpPassword: ['', [Validators.required]],
      termsAndCon: ['', [Validators.required]],
    });

    this.tooltipEnabler.enableTooltip();
  }

  onSubmitLogin(): void {
    if (this.loginForm.invalid) {
      this.submitFailed = true;
      return;
    }

    const formData = new FormData();
    formData.append('email', this.loginForm.get('email')?.value);
    formData.append('password', this.loginForm.get('password')!.value);

    this.http
      .post<HttpResponse<any>>(`${API_URL}/login`, formData, {
        observe: 'response',
      })
      .subscribe({
        //TODO: save token and id
        next: (response: any) => {
          if (response.body.Token) {
            const expirationDate = new Date();
            expirationDate.setTime(
              expirationDate.getTime() + 2 * 60 * 60 * 1000
            ); // 2 hours from now
            document.cookie = `sessionToken=${
              response.body.Token
            }; expires=${expirationDate.toUTCString()}; path=/`;
          }
        },
        error: (err) => {
          let statusMsg: string = err.error.status;
          const [errorMessage, errorTitle]: string[] =
            this.toastrResponse.getToastrRepsonse(statusMsg);
          this.toastr.error(errorMessage, errorTitle, {
            closeButton: true,
          });
        },
      });
  }

  onSubmitSignUp(): void {
    if (this.signUpForm.invalid) {
      this.signUpFailed = true;
      return;
    }

    const formData = new FormData();
    const cid = this.signUpForm.get('cid');
    if (cid) {
      formData.append('cid', cid.value);
    }

    const email = this.signUpForm.get('signUpemail');
    if (email) {
      formData.append('email', `${email.value}@chalmers.se`);
    }

    const password = this.signUpForm.get('signUpPassword');
    if (password) {
      formData.append('password', password.value);
    }

    this.http
      .post<HttpResponse<any>>(`${API_URL}/signUp`, formData, {
        observe: 'response',
      })
      .subscribe({
        next: (response: any) => {
          try {
            if (response.body.Token) {
              const expirationDate = new Date();
              expirationDate.setTime(
                expirationDate.getTime() + 2 * 60 * 60 * 1000
              ); // 2 hours from now
              document.cookie = `sessionToken=${
                response.body.Token
              }; expires=${expirationDate.toUTCString()}; path=/`;
            }

            this.toastr.success('Success!', 'User created!', {
              closeButton: true,
            });
          } catch {
            throw new Error('unexpected_error');
          }
        },
        error: (err) => {
          let statusMsg = err.error.status;
          const [errorMessage, errorTitle]: string[] =
            this.toastrResponse.getToastrRepsonse(statusMsg);
          this.toastr.error(errorMessage, errorTitle, {
            closeButton: true,
          });
        },
      });

    // Logic to submit the new user creation

    // TODO: Show visual feedback to user that account creation was successfull.

    this.signUpSuccess = true;
  }

  flipToSignUp() {
    const form = document.getElementById('flip-card-inner');
    if (form) {
      form.style.transform = 'rotateY(180deg)';
    }
  }

  flipToLogin() {
    const form = document.getElementById('flip-card-inner');
    if (form) {
      form.style.transform = 'rotateY(0deg)';
    }
  }

  flipTo(form: string) {
    const side = document.getElementById('flip-card-inner');
    if (side) {
      if (form == 'signUp') {
        side.style.transform = 'rotateY(180deg)';
      }
      if (form == 'login') {
        side.style.transform = 'rotateY(0deg)';
      }
    }
  }

  onInputFocus(input: string, form: FormGroup): void {
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
}
