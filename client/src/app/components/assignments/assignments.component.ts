import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Component, OnInit } from '@angular/core';
import { ActivatedRoute, NavigationEnd, Router } from '@angular/router';
import { Observable, switchMap } from 'rxjs';
import { Assignment, Course } from 'src/app/models/courses';
import { CourseService } from 'src/app/services/course-service.service';
import { API_URL } from 'src/environments/environment';
import { NgbModal } from '@ng-bootstrap/ng-bootstrap';
import { FileUploadModalComponent } from '../file-upload-modal/file-upload-modal.component';
import { SubmissionService } from 'src/app/services/submission.service';
import { GroupService } from 'src/app/services/group.service';
import { UserService } from 'src/app/services/user-service.service';
import { ToastrService } from 'ngx-toastr';
import { Group } from 'src/app/models/group';

@Component({
  selector: 'app-assignments',
  templateUrl: './assignments.component.html',
  styleUrls: ['./assignments.component.scss'],
})
export class AssignmentsComponent implements OnInit {
  course: Course = {} as Course;
  selectedTab: number = 0;
  group!: Group;
  courseGroups: Group[] = [];

  myGroup!: Group;
  isLoadingMap: Map<number, boolean> = new Map<number, boolean>();
  createGroupLoader: boolean = false;

  constructor(
    private route: ActivatedRoute,
    private courseService: CourseService,
    private http: HttpClient,
    private modalService: NgbModal,
    private submissionService: SubmissionService,
    private groupService: GroupService,
    private userService: UserService,
    private toastr: ToastrService
  ) {}

  ngOnInit() {
    const id = parseInt(this.route.snapshot.paramMap?.get('id') || '', 10);
    if (!isNaN(id)) {
      this.courseService.getCourse(id).subscribe((res: Course) => {
        this.course = res;
        console.log(this.course);
        this.course.Assignments.sort((a, b) => a.AssignmentNr - b.AssignmentNr);
      });
    }

    this.groupService.getMyGroup(id).subscribe((res) => {
      //TODO: HANDLE THE EMPTY GROUP BETTER, THIS FIX IS DUMB
      this.group = res;
    });

    this.groupService.getGroups(id).subscribe((res) => {
      this.courseGroups = res;
      console.log(this.courseGroups);
    });

    this.groupService.getMyGroup(id).subscribe((res) => {
      this.myGroup = res;
      console.log(res);
    });
  }

  get isAdmin(): boolean {
    return this.course.Role === 'Admin' || this.course.Role === 'Teacher';
  }

  onTabSelect(tabNumber: number): void {
    this.selectedTab = tabNumber;
  }

  goBack(): void {
    window.history.back();
  }

  openModal(courseId: number, groupId: number, assignmentNumber: number): void {
    const modalRef = this.modalService.open(FileUploadModalComponent);
    modalRef.componentInstance.name = 'fileUpload';
    modalRef.componentInstance.courseId = courseId;
    modalRef.componentInstance.groupId = groupId;
    modalRef.componentInstance.assignmentNumber = assignmentNumber;
  }

  formatDate(date: Date): string {
    return new Date(date).toLocaleDateString('sv-SE');
  }

  joinGroup(courseId: number, groupId: number): void {
    this.isLoadingMap.set(groupId, true);
    this.userService
      .getUserData()
      .pipe(
        switchMap((res) =>
          this.groupService.joinGroup(courseId, groupId, res.id)
        )
      )
      .subscribe({
        next: (res) => {
          console.log(res);
        },
        error: (err) => {
          this.isLoadingMap.set(groupId, false);
          this.toastr.error('Could not join group', 'Error');
        },
        complete: () => {
          this.isLoadingMap.set(groupId, false);
          location.reload();
        },
      });
  }

  removeFromGroup(courseId: number, groupId: number) {
    this.isLoadingMap.set(groupId, true);
    this.userService.getUserData().subscribe((res) => {
      this.groupService.removeFromGroup(courseId, groupId, res.id).subscribe({
        next: (res) => {
          console.log(res);
        },
        error: (err) => {
          this.isLoadingMap.set(groupId, false);
          this.toastr.error('Could not leave group', 'Error');
        },
        complete: () => {
          this.isLoadingMap.set(groupId, false);
          location.reload();
        },
      });
    });
  }

  createGroup(courseId: number) {
    this.createGroupLoader = true;
    this.groupService.createGroup(courseId).subscribe({
      next: (res) => {
        console.log(res);
      },
      error: (err) => {
        this.createGroupLoader = false;
        this.toastr.error('Error when creating group', 'Error');
      },
      complete: () => {
        this.createGroupLoader = false;
        location.reload();
      },
    });
  }

  // TODO: Handle in backend instead
  groupExists(): boolean {
    if (this.group) {
      if ('status' in this.group) {
        return false;
      } else {
        return true;
      }
    }
    return false;
  }
  // TODO: Bad
  hasGroup(): boolean {
    if (this.myGroup) {
      if ('status' in this.myGroup) {
        return false;
      } else {
        return true;
      }
    }
    return false;
  }

  inGroup(groupid: number): boolean {
    if (this.myGroup) {
      if ('status' in this.myGroup) {
        return false;
      } else {
        if (this.myGroup.groupId === groupid) {
          return true;
        } else return false;
      }
    }
    return false;
  }

  datePassed(date: Date): boolean {
    const now = new Date();
    now.setHours(0, 0, 0, 0);
    //to reset timeframes smaller than days
    // Check if the date has passed
    if (new Date(date).getTime() > now.getTime()) {
      return false;
    }
    return true;
  }
}
