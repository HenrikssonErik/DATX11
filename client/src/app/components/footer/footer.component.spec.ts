import { TestBed } from "@angular/core/testing";
import { FooterComponent } from "./footer.component";

describe('Testing Creating the footer component', () => { 
  beforeEach(() => {
    TestBed.configureTestingModule({
      imports: [],
      declarations: [FooterComponent],
    
    })
  })
  it('should create the footer-component',(() => {
    const fixture = TestBed.createComponent(FooterComponent);
    const app = fixture.debugElement.componentInstance;
    expect(app).toBeTruthy();
  }));
})