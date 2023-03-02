import { Component, OnInit } from '@angular/core';
import { FormBuilder, FormGroup, Validators } from '@angular/forms';

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

  constructor(private fb: FormBuilder) {}

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
    console.log(this.loginForm.get('password')?.value);

    const hashedpassword = this.hashPassword(
      this.loginForm.get('password')?.value
    );

    // Logic to submit form data to server
    //TODO: create method to hash password with bcrypt(done) -> send to backend -> handle response with/without token
    this.success = true;
  }

  onSubmitSignUp(): void {
    if (this.signUpForm.invalid) {
      this.signUpFailed = true;
      return;
    }

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
