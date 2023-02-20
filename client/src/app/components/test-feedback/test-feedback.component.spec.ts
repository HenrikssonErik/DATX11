import { TestBed } from "@angular/core/testing";
import { TestFeedbackComponent } from "./test-feedback.component";


describe('Testing Creating the Test-Feedback component', () => { 
  beforeEach(() => {
    TestBed.configureTestingModule({
      imports: [],
      declarations: [TestFeedbackComponent],
    
    })
  })
  it('should create the footer-component',(() => {
    const fixture = TestBed.createComponent(TestFeedbackComponent);
    const app = fixture.debugElement.componentInstance;
    expect(app).toBeTruthy();
  }));
})