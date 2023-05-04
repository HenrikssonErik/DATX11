import { HttpClient, HttpResponse } from '@angular/common/http';
import { Component, OnInit } from '@angular/core';
import {
  UntypedFormBuilder,
  UntypedFormGroup,
  Validators,
} from '@angular/forms';
import { Router } from '@angular/router';
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
  loginForm: UntypedFormGroup = new UntypedFormGroup({});
  signUpForm: UntypedFormGroup = new UntypedFormGroup({});
  submitFailed: boolean = false;
  cid: string = '';
  passwordVisible: boolean = false;
  verificationCidForm: UntypedFormGroup = new UntypedFormGroup({});

  constructor(
    private fb: UntypedFormBuilder,
    private http: HttpClient,
    private toastr: ToastrService,
    private tooltipEnabler: TooltipEnablerService,
    private toastrResponse: ToastrResponseService,
    public router: Router
  ) {}

  ngOnInit(): void {
    this.initializeLoginForm();
    this.initializeSignUpForm();
    this.initCid();
    this.enableTooltips();
  }

  private initializeLoginForm(): void {
    this.loginForm = this.fb.group({
      email: ['', [Validators.required, Validators.email]],
      password: ['', [Validators.required]],
      rememberMe: [false],
    });
  }

  private initCid(): void {
    this.verificationCidForm = this.fb.group({
      cid: ['', [Validators.required]],
    });
  }

  private initializeSignUpForm(): void {
    this.signUpForm = this.fb.group({
      cid: ['', [Validators.required]],
      signUpEmail: [''],
      signUpPassword: ['', [Validators.required]],
      termsAndCon: ['', [Validators.required]],
    });
  }

  private enableTooltips(): void {
    this.tooltipEnabler.enableTooltip();
  }

  onSubmitLogin(): void {
    if (this.loginForm.invalid) {
      this.submitFailed = true;
      return;
    }

    const formData = new FormData();
    const email = this.loginForm.get('email');
    const password = this.loginForm.get('password');

    if (email) {
      formData.append('email', email.value);
    }

    if (password) {
      formData.append('password', password.value);
    }

    this.http
      .post<HttpResponse<any>>(`${API_URL}/login`, formData, {
        observe: 'response',
      })
      .subscribe({
        next: (response: any) => {
          try {
            if (response.body.Token) {
              const expirationDate = new Date(Date.now() + 2 * 60 * 60 * 1000); //2 hours
              document.cookie = `Token=${
                response.body.Token
              }; expires=${expirationDate.toUTCString()}; path=/`;
              document.cookie = `Role=${
                response.body.GlobalRole
              }; expires=${expirationDate.toUTCString()}; path=/`;
            }
          } catch {
            throw new Error('unexpected_error');
          }
        },
        error: (err) => {
          let statusMsg: string = err.error.status;
          const [errorMessage, errorTitle]: string[] =
            this.toastrResponse.getToastrResponse(statusMsg);
          this.toastr.error(errorMessage, errorTitle, {
            closeButton: true,
          });
        },
        complete: () => {
          this.router.navigate(['/courses']);
        },
      });
  }

  public showPassword(inputForm: string) {
    this.passwordVisible = !this.passwordVisible;
    let obj = document.getElementById(inputForm) as HTMLInputElement;
    if (this.passwordVisible) {
      if (obj != null) {
        obj.type = 'text';
      }
    } else {
      if (obj != null) {
        obj.type = 'password';
      }
    }
  }

  onSubmitSignUp(): void {
    if (this.signUpForm.invalid) {
      return;
    }

    const formData = new FormData();
    const cid = this.signUpForm.get('cid');
    if (cid) {
      formData.append('cid', cid.value);
      formData.append('email', `${cid.value}@chalmers.se`);
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
              const expirationDate = new Date(Date.now() + 2 * 60 * 60 * 1000);
              document.cookie = `Token=${
                response.body.Token
              }; expires=${expirationDate.toUTCString()}; path=/`;
            }
          } catch {
            throw new Error('unexpected_error');
          }
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
          this.toastr.success(
            'You will now receive a verification email, click the link in the email to verify your account!',
            'User created!',
            {
              closeButton: true,
            }
          );
        },
      });
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

  onResendVerification(): void {
    if (this.verificationCidForm.invalid) {
      return;
    }

    const cidForm = new FormData();
    const cid = this.verificationCidForm.get('cid');
    if (cid) {
      cidForm.append('cid', cid.value);
    } else {
      return;
    }

    this.http
      .post<HttpResponse<any>>(`${API_URL}/resendVerification`, cidForm, {
        observe: 'response',
      })
      .subscribe({
        next: (response: any) => {},
        error: (err) => {
          let statusMsg = err.error.status;
          const [errorMessage, errorTitle]: string[] =
            this.toastrResponse.getToastrResponse(statusMsg);
          this.toastr.error(errorMessage, errorTitle, {
            closeButton: true,
          });
        },
        complete: () => {
          this.toastr.success(
            'Click the link in the email to verify your account!',
            'Verification mail has been sent!',
            {
              closeButton: true,
            }
          );
        },
      });
  }

  openVerificationModal(): void {
    this.verificationCidForm.reset();
  }
}
