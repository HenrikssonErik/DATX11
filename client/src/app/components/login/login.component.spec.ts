import { ComponentFixture, TestBed } from "@angular/core/testing";
import { FormBuilder, FormControl, FormGroup, Validators } from "@angular/forms";
import { LoginComponent } from "./login.component";

describe('Testing Creating the login component', () => { 
  beforeEach(() => {
    TestBed.configureTestingModule({
      imports: [],
      declarations: [LoginComponent],
      providers : [FormBuilder]
    })
  })
  it('should create the login component',(() => {
    const fixture = TestBed.createComponent(LoginComponent);
    const app = fixture.debugElement.componentInstance;
    expect(app).toBeTruthy();
  }));
})

describe('Testing the flip', () => {
  let loginComponent : LoginComponent;
  let fixture: ComponentFixture<LoginComponent>;
 
 
  beforeEach(() => {
    TestBed.configureTestingModule({
      imports: [],
      declarations: [LoginComponent],
      providers : [FormBuilder]
    })

    fixture = TestBed.createComponent(LoginComponent);
    loginComponent = fixture.componentInstance; 
    fixture.detectChanges();
    
  })

  it('should flip to login', () => {
    const form = document.createElement('div');
    form.id = 'flip-card-inner';
    spyOn(document, 'getElementById').and.returnValue(form);

    loginComponent.flipToLogin();

    expect(form.style.transform).toBe('rotateY(0deg)');
  });

  it('should flip to login', () => {
    const form = document.createElement('div');
    form.id = 'flip-card-inner';
    spyOn(document, 'getElementById').and.returnValue(form);

    loginComponent.flipToSignUp();

    expect(form.style.transform).toBe('rotateY(180deg)');
  });



  
})

describe('Testing effect on login/signup input', () => {
  let loginComponent : LoginComponent;
  let fixture: ComponentFixture<LoginComponent>;
  let form: FormGroup;
 

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ LoginComponent ],
      providers : [FormBuilder]
    })
    .compileComponents();
  });


  beforeEach(() => {
    fixture = TestBed.createComponent(LoginComponent);
    loginComponent = fixture.componentInstance;
    fixture.detectChanges();

    form = new FormGroup({
      email: new FormControl('', Validators.required),
      password: new FormControl('', Validators.required),
      rememberMe: new FormControl(false)
    });
  });

  it('should add success class to input when valid', () => {
    const input = 'email';
    const el = document.createElement('input');
    el.id = input;
    spyOn(document, 'getElementById').and.returnValue(el);

    form.controls[input].setValue('test@test.com');
    loginComponent.onInputFocus(input, form);

    expect(el.classList.contains('success')).toBeTrue();
    expect(el.classList.contains('error')).toBeFalse();
  });

  
  it('should remove success and error classes from input when not valid or invalid and not dirty or touched', () => {
    const input = 'email';
    const el = document.createElement('input');
    el.id = input;
    spyOn(document, 'getElementById').and.returnValue(el);

    form.controls[input].setValue('');
    loginComponent.onInputFocus(input, form);

    expect(el.classList.contains('success')).toBeFalse();
    expect(el.classList.contains('error')).toBeFalse();
  });

/*  it('should add error class to input when invalid and dirty or touched', () => {
    const input = 'email';
    const el = document.createElement('input');
    el.id = input;
    spyOn(document, 'getElementById').and.returnValue(el);

    form.controls[input].setValue('invalid_email');
    form.controls[input].markAsDirty();
    form.controls[input].markAsTouched();
    loginComponent.onInputFocus(input, form);

    expect(el.classList.contains('success')).toBeFalse();
    expect(el.classList.contains('error')).toBeTrue();
  });  */
})