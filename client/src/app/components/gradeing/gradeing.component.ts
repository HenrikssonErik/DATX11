import { Component } from '@angular/core';
import { SubmissionService } from 'src/app/services/submission.service';

@Component({
  selector: 'app-gradeing',
  templateUrl: './gradeing.component.html',
  styleUrls: ['./gradeing.component.scss'],
})
export class GradeingComponent {
  constructor(private submissionService: SubmissionService) {}
}
