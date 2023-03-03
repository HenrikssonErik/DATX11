import { HttpClient, HttpResponse } from '@angular/common/http';
import { Component, OnInit } from '@angular/core';
import { FormBuilder, FormGroup, Validators } from '@angular/forms';
import { ToastrService } from 'ngx-toastr';
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

  constructor(
    private fb: FormBuilder,
    private http: HttpClient,
    private toastr: ToastrService
  ) {}

  ngOnInit(): void {
    this.loginForm = this.fb.group({
      email: ['', [Validators.required, Validators.email]],
      password: ['', [Validators.required]],
      rememberMe: [false],
    });

    this.signUpForm = this.fb.group({
      cid: ['', [Validators.required]],
      signUpemail: ['', [Validators.required, Validators.email]],
      signUpPassword: ['', [Validators.required]],
      termsAndCon: ['', [Validators.required]],
    });
  }

  onSubmitLogin(): void {
    if (this.loginForm.invalid) {
      this.submitFailed = true;
      return;
    }
    // Logic to submit login

    const hashedpassword = this.hashPassword(
      this.loginForm.get('password')?.value
    );
    console.log('hashed: ' + hashedpassword);
    const formData = new FormData();
    formData.append('email', this.loginForm.get('email')?.value);
    formData.append('password', hashedpassword);
    console.log(formData.get('password'));

    this.http
      .post<HttpResponse<any>>(`${API_URL}/` + 'login', formData, {
        observe: 'response',
      })
      .subscribe({
        //TODO: save token and id
        next: (response: any) => {
          console.log(response);
        },
      });

    //TODO: this.success = true;
  }

  onSubmitSignUp(): void {
    if (this.signUpForm.invalid) {
      this.signUpFailed = true;
      return;
    }

    const hashedpassword = this.hashPassword(
      this.signUpForm.get('signUpPassword')!.value
    );
    console.log('hashed: ' + hashedpassword);
    const formData = new FormData();
    formData.append('cid', this.signUpForm.get('cid')!.value);
    formData.append('email', this.signUpForm.get('signUpemail')!.value);
    formData.append('password', hashedpassword);
    console.log(formData.get('password'));

    this.http
      .post<HttpResponse<any>>(`${API_URL}/` + 'signUp', formData, {
        observe: 'response',
      })
      .subscribe({
        next: (response: any) => {
          this.toastr.success('Success!', 'User created!', {
            closeButton: true,
          });
        },
        error: (err) => {
          if (err.error.status === 'already_registered')
            this.toastr.error(
              'You seem to be registered already. Have you forgotten your password?',
              'User with that CID is already registered!',
              {
                closeButton: true,
              }
            );
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

  hashPassword(password: string): string {
    const hash: string = this.bcrypt.hashSync(password, 10);
    return hash;
  }

  onInputFocus(input: string, form: FormGroup): void {
    const control = form.get(input);

    if (control) {
      const isValid = control.valid;
      const isInvalid = control.invalid && (control.dirty || control.touched);
      const el = document.getElementById(input);
      if (isValid) {
        el?.classList.add('success');
        el?.classList.remove('error');
      } else if (isInvalid) {
        el?.classList.add('error');
        el?.classList.remove('success');
      } else {
        el?.classList.remove('success');
        el?.classList.remove('error');
      }
    }
  }
}
