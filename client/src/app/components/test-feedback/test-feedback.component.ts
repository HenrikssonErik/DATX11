import {
  Component,
  Input,
  OnChanges,
  OnInit,
  SimpleChanges,
} from '@angular/core';

@Component({
  selector: 'app-test-feedback',
  templateUrl: './test-feedback.component.html',
  styleUrls: ['./test-feedback.component.scss'],
})
export class TestFeedbackComponent implements OnInit {
  @Input() feedbackFiles: any;

  constructor() {}

  ngOnInit(): void {
    /* Should (of course) be done dynamically in the future */
  }
}
