import { Component, OnInit } from '@angular/core';
import { FormBuilder, FormGroup, Validators } from '@angular/forms';

@Component({
  selector: 'app-login',
  templateUrl: './login.component.html',
  styleUrls: ['./login.component.scss'],
})
export class LoginComponent implements OnInit {
  loginForm: FormGroup = new FormGroup({});
  submitFailed: boolean = false;
  success: boolean = false;
  bcrypt = require('bcryptjs');

  constructor(private fb: FormBuilder) {}

  ngOnInit(): void {
    this.loginForm = this.fb.group({
      email: ['', [Validators.required, Validators.email]],
      password: ['', [Validators.required]],
      rememberMe: [false],
    });
  }

  onSubmit() {
    console.log('onSubmit');
    if (this.loginForm.invalid) {
      this.submitFailed = true;

      return;
    }
    console.log(this.loginForm.get('password')?.value);

    const hashedpassword = this.hashPassword(
      this.loginForm.get('password')?.value
    );

    // Logic to submit form data to server
    //TODO: create method to hash password with bcrypt(done) -> send to backend -> handle response with/without token

    this.success = true;
  }

  hashPassword(password: string): string {
    const hash: string = this.bcrypt.hashSync(password, 10);
    return hash;
  }

  onInputFocus(input: string) {
    const control = this.loginForm.get(input);

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
