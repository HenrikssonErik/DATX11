import { DebugElement, Renderer2 } from "@angular/core"
import { ComponentFixture, TestBed } from "@angular/core/testing"
import { By } from "@angular/platform-browser"
import { NavbarComponent } from "./navbar.component"

describe('Testing creating the navbar component', () => {
  beforeEach(() => {
    TestBed.configureTestingModule({
      imports: [],
      declarations: [NavbarComponent],
      providers : [Renderer2]
    })
  })
  it('should create the component NavbarComponent', (() => {
    const fixture = TestBed.createComponent(NavbarComponent);
    const app = fixture.debugElement.componentInstance;
    // Check that the component exists
    expect(app).toBeTruthy();
  }))
})


describe('Testing the navbar scroll effect', () => {
  let fixture: ComponentFixture<NavbarComponent>;
  let component: NavbarComponent;
  let renderer: Renderer2;
  beforeEach(async() => {
    await TestBed.configureTestingModule({
      providers: [Renderer2],
      declarations: [NavbarComponent],
    }).compileComponents();
  })

  beforeEach(() => {
    fixture = TestBed.createComponent(NavbarComponent);
    component = fixture.componentInstance;
    renderer = TestBed.inject(Renderer2);
    fixture.detectChanges();
  });

  it('should add affix class to nav when scrolled below 50 pixels', () => {
    // Mock the DOM element
    spyOn(document, 'querySelector').and.returnValue({
      classList: { add: jasmine.createSpy('add'), remove: jasmine.createSpy('remove') } as unknown as DOMTokenList,
    } as Element);
  
    // Call the ngOnInit method and simulate scrolling below 50 pixels
    component.ngOnInit();
    Object.defineProperty(window, 'scrollY', { value: 49 });
    window.dispatchEvent(new Event('scroll'));
    const navElement = document.querySelector('.nav');

    // Expect that the classList.add method was not called
    if (navElement) {
      expect(navElement.classList.add).not.toHaveBeenCalled();
    }
    
    // Simulate scrolling above 50 pixels and expect that classList.add and classList.remove were called
    Object.defineProperty(window, 'scrollY', { value: 51 });
    window.dispatchEvent(new Event('scroll'));
    
    // Expect that the classlist.add was called
    if(navElement){
      expect(navElement.classList.add).toHaveBeenCalledWith('affix');
      expect(navElement.classList.remove).toHaveBeenCalled();
    }
  });
})

describe('Testing the navbar mobile click', () => {
  let fixture: ComponentFixture<NavbarComponent>;
  let component: NavbarComponent;
  let navTrigger: DebugElement;

  beforeEach(async() => {
    await TestBed.configureTestingModule({
      providers: [Renderer2],
      declarations: [NavbarComponent],
    }).compileComponents();
  })

  beforeEach(() => {
    fixture = TestBed.createComponent(NavbarComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();

    // Find the navTrigger element by its class
    navTrigger = fixture.debugElement.query(By.css('.navTrigger'));
  });

  it('should toggle active class and show menu', () => {
    // Click the navTrigger element
    navTrigger.nativeElement.click();
    fixture.detectChanges();

    // Check that the navTrigger element has the "active" class
    expect(navTrigger.nativeElement.classList.contains('active')).toBeTrue();

    // Check that the mainListDiv element has the "show_list" class
    const mainListDiv = fixture.debugElement.query(By.css('#mainListDiv'));
    expect(mainListDiv.nativeElement.classList.contains('show_list')).toBeTrue();
  });

  it('should toggle active class and hide menu', () => {
    // Click the navTrigger element twice
    navTrigger.nativeElement.click();
    fixture.detectChanges();
    navTrigger.nativeElement.click();
    fixture.detectChanges();

    // Check that the navTrigger element does not have the "active" class
    expect(navTrigger.nativeElement.classList.contains('active')).toBeFalse();

    // Check that the mainListDiv element does not have the "show_list" class
    const mainListDiv = fixture.debugElement.query(By.css('#mainListDiv'));
    expect(mainListDiv.nativeElement.classList.contains('show_list')).toBeFalse();
  });
});

