import { Component, Input } from '@angular/core';
import { Course } from 'src/app/models/courses';
import { SubmissionService } from 'src/app/services/submission.service';

@Component({
  selector: 'app-gradeing',
  templateUrl: './gradeing.component.html',
  styleUrls: ['./gradeing.component.scss'],
})
export class GradeingComponent {
  @Input() course!: Course;

  constructor(private submissionService: SubmissionService) {}

  ngOnInit(): void {
    this.submissionService
      .getAssignmentOverView(this.course.courseID, 2)
      .subscribe((data) => {
        console.log(data);
      });
  }
}
