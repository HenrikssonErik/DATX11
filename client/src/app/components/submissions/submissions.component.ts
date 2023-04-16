import { Component, Input } from '@angular/core';
import { SubmissionService } from 'src/app/services/submission.service';
import { Submission } from 'src/app/models/submission';

@Component({
  selector: 'app-submissions',
  templateUrl: './submissions.component.html',
  styleUrls: ['./submissions.component.scss'],
})
export class SubmissionsComponent {
  @Input() assignmentNr!: number;
  @Input() courseId!: number;
  submissions!: Submission[];
  isLoading: boolean = false;
  constructor(private submissionService: SubmissionService) {}

  ngOnInit(): void {
    this.getSubmissions();
  }

  getSubmissions() {
    this.isLoading = true;
    this.submissionService
      .getSubmission(this.courseId, this.assignmentNr)
      .subscribe({
        next: (res: Submission[]) => {
          this.submissions = res;
        },
        error: (err) => {
          console.log(err);
          this.isLoading = false;
        },
        complete: () => {
          this.isLoading = false;
          console.log(this.submissions);
        },
      });
  }

  /*   getSubmissions() {
    this.isLoading = true;
    this.submissionService
      .getSubmission(this.courseId, this.assignmentNr)
      .subscribe((res: ) => {
        this.submissions = res;
        this.isLoading = false;
        console.log(this.submissions);
      });
  } */
}
