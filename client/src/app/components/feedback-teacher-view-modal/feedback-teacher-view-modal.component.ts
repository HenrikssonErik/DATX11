import { Component, Input } from '@angular/core';
import { SubmissionService } from 'src/app/services/submission.service';

@Component({
  selector: 'app-feedback-teacher-view-modal',
  templateUrl: './feedback-teacher-view-modal.component.html',
  styleUrls: ['./feedback-teacher-view-modal.component.scss'],
})
export class FeedbackTeacherViewModalComponent {
  @Input() assignmentNr!: number;
  @Input() courseId!: number;
  @Input() group!: number;

  constructor(private submissionService: SubmissionService) {}

  ngOnInit(): void {
    this.submissionService
      .getTestingFeedback(this.courseId, this.assignmentNr, this.group)
      .subscribe({
        next: (data: any) => {
          console.log(data);
        },
        error: (error) => {
          console.error('Failed to get data:', error);
        },
        complete: () => {
          console.log('complete');
        },
      });
  }
}
