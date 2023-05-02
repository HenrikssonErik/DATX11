import { Component, Input } from '@angular/core';
import { Course } from 'src/app/models/courses';
import { SubmissionService } from 'src/app/services/submission.service';
import { AssignmentSubmission, Submission } from 'src/app/models/submission';
import { Subject } from 'rxjs';
import { debounceTime } from 'rxjs/operators';
import { NgbModal } from '@ng-bootstrap/ng-bootstrap';
import { FeedbackTeacherViewModalComponent } from '../feedback-teacher-view-modal/feedback-teacher-view-modal.component';

@Component({
  selector: 'app-gradeing',
  templateUrl: './gradeing.component.html',
  styleUrls: ['./gradeing.component.scss'],
})
export class GradeingComponent {
  searchTerm$: Subject<string> = new Subject<string>();
  @Input() course!: Course;
  //TODO: Rename
  gradeingSubmission?: Submission;
  assignmentNumbers?: number[];
  selectedAssignment?: number;
  selectedAssignmentIndex?: number;
  allAssignments?: Submission[];
  searchText: string = '';
  commentText: string = '';

  constructor(
    private submissionService: SubmissionService,
    private modalService: NgbModal
  ) {}

  ngOnInit(): void {
    this.submissionService
      .getAssignmentOverView(this.course.courseID)
      .subscribe({
        next: (data: Submission[]) => {
          this.allAssignments = data;
          this.assignmentNumbers = this.getAssignmentNumbers(data);
          this.setAssignmentToGrade(data[0]);
        },
        error: (error) => {
          console.error('Failed to get data:', error);
        },
        complete: () => {
          if (this.allAssignments) {
            this.initSearch();
          }
        },
      });
  }

  filterAssignments(assignmentNr: number) {
    this.selectedAssignment = assignmentNr;
    this.getSelectedAssignmentIndex();
    if (this.allAssignments) {
      this.gradeingSubmission = this.allAssignments.find(
        (assignment: Submission): boolean =>
          assignment.Assignment === assignmentNr
      )!;
    }
    //TODO: handle if it was not found
    if (this.gradeingSubmission) {
      // Assignment was found
      console.log(this.gradeingSubmission);
    } else {
      // Assignment was not found
    }
  }

  openFeedBackModal(group: number, assignmentNr: number) {
    const modalRef = this.modalService.open(FeedbackTeacherViewModalComponent);
    modalRef.componentInstance.name = 'feedbackTeacherViewModalComponent';
    modalRef.componentInstance.group = group;
    modalRef.componentInstance.assignmentNr = assignmentNr;
    modalRef.componentInstance.courseId = this.course.courseID;
  }

  setAssignmentToGrade(assignment: Submission) {
    //TODO: Make sure that the init with 1 is ok. It probably is not.
    this.filterAssignments(1);
    this.gradeingSubmission = assignment;
  }

  getAssignmentNumbers(data: Submission[]): number[] {
    return data.map((sub: Submission): number => sub.Assignment);
  }

  initSearch() {
    this.searchTerm$.pipe(debounceTime(200)).subscribe((searchTerm: string) => {
      if (!searchTerm && this.allAssignments) {
        if (this.selectedAssignmentIndex) {
          this.gradeingSubmission =
            this.allAssignments[this.selectedAssignmentIndex];
          return;
        } else {
          this.gradeingSubmission = this.allAssignments[0];
          return;
        }
      }
      this.gradeingSubmission = this.allAssignments?.find((assignment) => {
        return assignment.Submissions.some((submission) => {
          return submission.groupid.toString().includes(searchTerm);
        });
      });
      //TODO: handle if it was not found. Right now it will just be undefined :(
      console.log(this.gradeingSubmission);
    });
  }

  onSearchTextChanged() {
    this.searchTerm$.next(this.searchText);
  }

  getSelectedAssignmentIndex() {
    if (this.allAssignments) {
      this.selectedAssignmentIndex = this.allAssignments.findIndex(
        (assignment) => {
          return assignment.Assignment === this.selectedAssignment;
        }
      );
    }
  }

  setSubmissionGrade(
    submission: AssignmentSubmission,
    assignmentNr: number,
    grade: boolean
  ) {
    this.submissionService
      .setFeedback(
        this.course.courseID,
        assignmentNr,
        submission.Submission,
        this.commentText,
        grade,
        submission.groupid
      )
      .subscribe({
        next: (data: any) => {
          console.log(data);
        },
        error: (err) => {
          console.log(err);
        },
        complete: () => {
          console.log('done');
        },
      });
  }
}