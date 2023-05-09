import { Component, Input } from '@angular/core';
import { Course } from 'src/app/models/courses';
import { SubmissionService } from 'src/app/services/submission.service';
import { AssignmentSubmission, Submission } from 'src/app/models/submission';
import { Subject } from 'rxjs';
import { debounceTime, takeUntil } from 'rxjs/operators';
import { NgbModal } from '@ng-bootstrap/ng-bootstrap';
import { FeedbackTeacherViewModalComponent } from '../feedback-teacher-view-modal/feedback-teacher-view-modal.component';
import { FormControl, FormGroup } from '@angular/forms';
import { TooltipEnablerService } from 'src/app/services/tooltip-enabler.service';
import { ToastrService } from 'ngx-toastr';
import { GroupService } from 'src/app/services/group.service';
import { CourseService } from 'src/app/services/course-service.service';

@Component({
  selector: 'app-gradeing',
  templateUrl: './grading.component.html',
  styleUrls: ['./grading.component.scss'],
})
export class GradingComponent {
  searchTerm$: Subject<string> = new Subject<string>();
  unsubscribe$: Subject<void> = new Subject();
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
  //TODO: Add type @Kvalle99
  groupMembers: any = {};
  isLoading: boolean = false;

  constructor(
    private submissionService: SubmissionService,
    private modalService: NgbModal,
    private tooltipEnabler: TooltipEnablerService,
    private toastr: ToastrService,
    private groupService: GroupService
  ) {}

  ngOnInit(): void {
    this.getSubmissions();
    this.setSelectedAssignment();
    this.initForm();
    this.enableTooltips();
  }

  ngAfterViewInit(): void {
    this.isLoading = true;
    this.waitForData().then((): void => {
      this.filter();
    });
  }

  waitForData(): Promise<void> {
    return new Promise((resolve) => {
      const checkData = setInterval(() => {
        if (this.allAssignments && this.selectedAssignment) {
          clearInterval(checkData);
          resolve();
        }
      }, 100);
    });
  }

  getSubmissions() {
    this.submissionService
      .getAssignmentOverView(this.course.courseID)
      .subscribe({
        next: (data: Submission[]) => {
          this.allAssignments = data;
          this.assignmentNumbers = this.getAssignmentNumbers(data);
          this.isLoading = false;
        },
        error: (error) => {
          console.error('Failed to get data:', error);
        },
        complete: () => {
          if (this.allAssignments) {
            //this.initSearch();
          }
        },
      });
  }

  initForm(): void {
    this.form = new FormGroup({
      gradeAgain: new FormControl(false),
    });
  }

  setSelectedAssignmentIndex(assignmentNr: number): void {
    this.selectedAssignment = assignmentNr;
  }

  setGradedBoolean(graded: boolean): void {
    this.sortGraded = graded;
  }

  setDateSort(sort: string): void {
    this.dateFilter = sort;
  }

  setSelectedAssignment() {
    if (this.course.Assignments.length > 0) {
      this.selectedAssignment = this.course.Assignments[0].AssignmentNr;
    }
  }

  private enableTooltips(): void {
    this.tooltipEnabler.enableTooltip();
  }

  filterAssignment(submissions: Submission[]): Submission[] {
    if (this.selectedAssignment) {
      return submissions.filter((submission) => {
        return submission.Assignment === this.selectedAssignment;
      });
    }
    return submissions;
  }

  filterGraded(submissions: AssignmentSubmission[]): AssignmentSubmission[] {
    console.log(submissions);
    if (this.sortGraded) {
      return submissions.filter((submission) => {
        return submission.grade !== null;
      });
    } else {
      return submissions.filter((submission) => submission.grade === null);
    }
  }

  filterDate(submissions: AssignmentSubmission[]): AssignmentSubmission[] {
    const tempList: AssignmentSubmission[] = submissions.sort((a, b) => {
      const dateA = new Date(a.dateSubmitted);
      const dateB = new Date(b.dateSubmitted);
      if (this.dateFilter === 'ASC') {
        if (dateA.getTime() < dateB.getTime()) {
          return -1;
        } else if (dateA.getTime() > dateB.getTime()) {
          return 1;
        } else {
          return 0;
        }
      } else {
        if (dateA.getTime() < dateB.getTime()) {
          return 1;
        } else if (dateA.getTime() > dateB.getTime()) {
          return -1;
        } else {
          return 0;
        }
      }
    });
    return tempList;
  }

  filterSearch() {
    this.searchTerm$
      .pipe(takeUntil(this.unsubscribe$), debounceTime(200))
      .subscribe((searchTerm: string) => {
        console.log(searchTerm);
        if (this.gradeingSubmission) {
          console.log(this.gradeingSubmission);
          this.gradeingSubmission = this.gradeingSubmission[0].filter(
            (submission) =>
              submission.GroupNumber.toString().includes(searchTerm)
          );
        }
      });
  }

  filter(): void {
    if (this.allAssignments && this.selectedAssignment) {
      let tempList: Submission[] = this.allAssignments?.slice();
      tempList = this.filterAssignment(tempList);
      let tempListSubmissions: AssignmentSubmission[] =
        tempList[0].Submissions.slice();
      tempListSubmissions = this.filterGraded(tempListSubmissions);
      tempListSubmissions = this.filterDate(tempListSubmissions);
      this.isLoading = false;
      this.gradeingSubmission = {
        ...tempList[0],
        Submissions: tempListSubmissions,
      };
      this.filterSearch();
      this.setFileNames(this.selectedAssignment);
    }
  }

  getMaxScore(assignmentNr: number): number {
    const assignment = this.course.Assignments.find(
      (assignment) => assignment.AssignmentNr === assignmentNr
    );
    return assignment?.MaxScore ?? 1;
  }

  setFileNames(assignmentNr: number) {
    this.getFileNames(assignmentNr);
  }

  openFeedBackModal(
    groupId: number,
    assignmentNr: number,
    groupNumber: number
  ) {
    const modalRef = this.modalService.open(FeedbackTeacherViewModalComponent);
    modalRef.componentInstance.name = 'feedbackTeacherViewModalComponent';
    modalRef.componentInstance.groupId = groupId;
    modalRef.componentInstance.groupNumber = groupNumber;
    modalRef.componentInstance.assignmentNr = assignmentNr;
    modalRef.componentInstance.courseId = this.course.courseID;
  }

  getAssignmentNumbers(data: Submission[]): number[] {
    return data.map((sub: Submission): number => sub.Assignment);
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
          this.toastr.error('Could not set grade', 'Error!');
        },
        complete: () => {
          this.toastr.success(
            'The assignment was successfully graded!',
            'Success!',
            {
              closeButton: true,
            }
          );
        },
      });
  }

  getGroupMembers(group: number) {
    //TODO: Fattar fortfarande inte vafan som händer här. Varför returnas alltid en tom array?
    //Borde inte returna nåt imo? HTMLen bryr väl sig ändå bara om this.groupMembers?
    this.groupService.getGroup(group, this.course.courseID).subscribe({
      next: (data: any) => {
        console.log(data);
        this.groupMembers[group] = data['users'];
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

  ngOnDestroy() {
    this.unsubscribe$.next();
    this.unsubscribe$.complete();
  }
}
