import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Component, OnInit } from '@angular/core';
import { ActivatedRoute, NavigationEnd, Router } from '@angular/router';
import { Observable } from 'rxjs';
import { Assignment, Course } from 'src/app/models/courses';
import { CourseService } from 'src/app/services/course-service.service';
import { API_URL } from 'src/environments/environment';
import { NgbModal } from '@ng-bootstrap/ng-bootstrap';
import { FileUploadModalComponent } from '../file-upload-modal/file-upload-modal.component';
import { SubmissionService } from 'src/app/services/submission.service';
import { GroupService } from 'src/app/services/group.service';
import { UserService } from 'src/app/services/user-service.service';

@Component({
  selector: 'app-assignments',
  templateUrl: './assignments.component.html',
  styleUrls: ['./assignments.component.scss'],
})
export class AssignmentsComponent implements OnInit {
  course: Course = {} as Course;
  selectedTab: number = 0;
  //TODO: Create a Model for group
  group: any;
  courseGroups: { groupId: number; groupNumber: number; users: string[] }[] =
    [];

  myGroup: any;
  isLoading: boolean = false;
  createGroupLoader: boolean = false;

  constructor(
    private route: ActivatedRoute,
    private courseService: CourseService,
    private http: HttpClient,
    private modalService: NgbModal,
    private submissionService: SubmissionService,
    private groupService: GroupService,
    private userService: UserService
  ) {}

  ngOnInit() {
    const id = parseInt(this.route.snapshot.paramMap?.get('id') || '', 10);
    if (!isNaN(id)) {
      this.courseService.getCourse(id).subscribe((res: Course) => {
        this.course = res;
      });
    }

    this.getGroup(id).subscribe((res: Course) => {
      //TODO: HANDLE THE EMPTY GROUP BETTER, THIS FIX IS DUMB

      this.group = res;
    });

    this.submissionService.getSubmission(1, 1).subscribe((res) => {
      console.log(res);
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

  getGroup(id: number): Observable<Course> {
    const headers = new HttpHeaders()
      .append('Cookies', document.cookie)
      .set('Cache-Control', 'public, max-age=3600');
    return this.http.get<Course>(`${API_URL}/getMyGroup?Course=${id}`, {
      headers,
    });
  }
  formatDate(date: Date): string {
    return new Date(date).toLocaleDateString('sv-SE');
  }

  joinGroup(courseId: number, groupId: number): void {
    this.isLoading = true;
    this.userService.getUserData().subscribe((res) => {
      console.log(res);
      this.groupService.joinGroup(courseId, groupId, res.id).subscribe({
        next: (res) => {
          console.log(res);
        },

        error: (err) => {
          console.log(err);
        },
        complete: () => {
          this.isLoading = false;
          location.reload();
        },
      });
    });
  }

  removeFromGroup(courseId: number, groupId: number) {
    this.isLoading = true;
    this.userService.getUserData().subscribe((res) => {
      this.groupService.removeFromGroup(courseId, groupId, res.id).subscribe({
        next: (res) => {
          console.log(res);
        },
        error: (err) => {
          console.log(err);
        },
        complete: () => {
          this.isLoading = false;
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
        console.log(err);
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
      } else if (this.group.length === 0) {
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
}
