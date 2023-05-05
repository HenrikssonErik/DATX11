import { Component, Input } from '@angular/core';
import { Course } from 'src/app/models/courses';
import { SubmissionService } from 'src/app/services/submission.service';
import { AssignmentSubmission, Submission } from 'src/app/models/submission';
import { Subject } from 'rxjs';
import { debounceTime } from 'rxjs/operators';
import { NgbModal } from '@ng-bootstrap/ng-bootstrap';
import { FeedbackTeacherViewModalComponent } from '../feedback-teacher-view-modal/feedback-teacher-view-modal.component';
import { FormControl, FormGroup } from '@angular/forms';
import { TooltipEnablerService } from 'src/app/services/tooltip-enabler.service';
import { ToastrService } from 'ngx-toastr';
import { GroupService } from 'src/app/services/group.service';

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
  score: number = 1;
  fileNames?: string[];
  form!: FormGroup;
  sortGraded: boolean = false;
  dateFilter: string = '';

  constructor(
    private submissionService: SubmissionService,
    private modalService: NgbModal,
    private tooltipEnabler: TooltipEnablerService,
    private toastr: ToastrService,
    private groupService: GroupService
  ) {}

  ngOnInit(): void {
    this.form = new FormGroup({
      gradeAgain: new FormControl(false),
    });

    this.enableTooltips();

    this.setSelectedAssignment();

    //TODO: Break out into a function
    this.submissionService
      .getAssignmentOverView(this.course.courseID)
      .subscribe({
        next: (data: Submission[]) => {
          this.allAssignments = data;
          this.assignmentNumbers = this.getAssignmentNumbers(data);
          //this.setAssignmentToGrade(data[0]);
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

  setSelectedAssignmentIndex(assignmentNr: number) {
    this.selectedAssignment = assignmentNr;
  }

  setSelectedAssignment() {
    if (this.course.Assignments.length > 0) {
      this.selectedAssignment = this.course.Assignments[0].AssignmentNr;
    }
  }

  private enableTooltips(): void {
    this.tooltipEnabler.enableTooltip();
  }

  filterAssignments(assignmentNr: number) {
    this.selectedAssignment = assignmentNr;
    this.getSelectedAssignmentIndex();
    if (this.allAssignments) {
      this.gradeingSubmission = this.allAssignments.find(
        (assignment: Submission): boolean =>
          assignment.Assignment === assignmentNr
      )!;
      this.setFileNames(assignmentNr);
    }
    //TODO: handle if it was not found
    if (this.gradeingSubmission) {
      // Assignment was found
      console.log(this.gradeingSubmission);
    } else {
      // Assignment was not found
    }
  }

  filterAssignment(submissions: Submission[]): Submission[] {
    if (this.selectedAssignment) {
      this.setFileNames(this.selectedAssignment);
      return submissions.filter((submission) => {
        return submission.Assignment === this.selectedAssignment;
      });
    }
    return submissions;
  }

  filterGraded(submissions: Submission[]): Submission[] {
    const tempList: Submission[] = submissions.filter(
      (submission: Submission): boolean => {
        return submission.Submissions.some(
          (submission: AssignmentSubmission): boolean => {
            return submission.grade != this.sortGraded;
          }
        );
      }
    );
    return tempList;
  }

  filterDate(submissions: Submission[]): Submission[] {
    const tempList: Submission[] = submissions.sort((a, b) => {
      const dateA = new Date(a.Submissions[0].Date);
      const dateB = new Date(b.Submissions[0].Date);

      if (this.dateFilter === 'ASC') {
        return dateA.getTime() - dateB.getTime();
      } else {
        return dateB.getTime() - dateA.getTime();
      }
    });
    return tempList;
  }

  filter() {
    if (this.allAssignments) {
      let tempList: Submission[] = this.allAssignments?.slice();
      console.log('All:', tempList);
      tempList = this.filterAssignment(tempList);
      console.log('after filterassignment:', tempList);
      tempList = this.filterGraded(tempList);
      console.log('After filted graded:', tempList);
      tempList = this.filterDate(tempList);
      console.log('After filted date:', tempList);
      this.gradeingSubmission = tempList[0];
      console.log('Gradeingsubmission', this.gradeingSubmission);
    }
  }

  getMaxScore(assignmentNr: number): number {
    const assignment = this.course.Assignments.find(
      (assignment) => assignment.AssignmentNr === assignmentNr
    );
    return assignment?.MaxScore ?? 0;
  }

  setFileNames(assignmentNr: number) {
    this.getFileNames(assignmentNr);
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
    console.log(this.commentText);
    this.submissionService
      .setFeedback(
        this.course.courseID,
        assignmentNr,
        submission.Submission,
        this.commentText,
        grade,
        submission.groupid,
        this.score
      )
      .subscribe({
        next: (data: any) => {
          //TODO: ADD TO SUBMISSIONS?
        },
        error: (err) => {
          console.log(err);
          this.toastr.error('Something went wrong!', 'Error!');
        },
        complete: () => {
          this.toastr.success(
            'The assignment was succesfully graded!',
            'Sucess!',
            {
              closeButton: true,
            }
          );
        },
      });
  }

  getGroupMembers(group: number): string[] {
    this.groupService.getGroupMembers(group, this.course.courseID).subscribe({
      next: (data: any) => {
        console.log(data);
        return data;
      },
      error: (err) => {
        console.log(err);
        return [];
      },
    });

    return [];
  }

  getFileNames(assignmentNr: number) {
    this.submissionService
      .getFileNames(this.course.courseID, assignmentNr)
      .subscribe({
        next: (data: any) => {
          this.fileNames = data.Filenames;
        },
        error: (err) => {
          console.log(err);
        },
      });
  }

  downloadSubmissionFile(
    groupId: number,
    assignmentNr: number,
    submissionId: number,
    fileName: string
  ) {
    this.submissionService.downloadSubmissionFile(
      this.course.courseID,
      groupId,
      assignmentNr,
      submissionId,
      fileName
    );
  }

  getDate(date: string) {
    return new Date(date).toLocaleDateString('sv-SE');
  }
}
