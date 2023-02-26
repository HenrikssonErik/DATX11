import { Component, OnInit } from '@angular/core';
import { FormBuilder, FormGroup, Validators } from '@angular/forms';

@Component({
  selector: 'app-login',
  templateUrl: './login.component.html',
  styleUrls: ['./login.component.scss']
})
export class LoginComponent implements OnInit {

  loginForm: FormGroup = new FormGroup({});
  submitFailed: boolean = false;
  success: boolean = false;

  constructor(private fb: FormBuilder) {
  
  }
  



  ngOnInit(): void {
    this.loginForm = this.fb.group({
      email: ['', [Validators.required, Validators.email]],
      password: ['', [Validators.required]],
      rememberMe: [false]
    });
  
  }

  onSubmit() {
    if (this.loginForm.invalid) {
      this.submitFailed = true;
      return;
    }

    // Logic to submit form data to server

    this.success = true;
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
