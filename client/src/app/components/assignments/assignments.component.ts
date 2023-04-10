import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Component, OnInit } from '@angular/core';
import { ActivatedRoute, NavigationEnd, Router } from '@angular/router';
import { Observable } from 'rxjs';
import { Assignment, Course } from 'src/app/models/courses';
import { CourseService } from 'src/app/services/course-service.service';
import { API_URL } from 'src/environments/environment';
import { NgbModal } from '@ng-bootstrap/ng-bootstrap';
import { FileUploadModalComponent } from '../file-upload-modal/file-upload-modal.component';

@Component({
  selector: 'app-assignments',
  templateUrl: './assignments.component.html',
  styleUrls: ['./assignments.component.scss'],
})
export class AssignmentsComponent implements OnInit {
  course: Course = {} as Course;
  selectedTab: number = 0;
  group: any;

  constructor(
    private route: ActivatedRoute,
    private courseService: CourseService,
    private http: HttpClient,
    private modalService: NgbModal
  ) {}

  ngOnInit() {
    const id = parseInt(this.route.snapshot.paramMap?.get('id') || '', 10);
    if (!isNaN(id)) {
      this.courseService.getCourse(id).subscribe((res: Course) => {
        this.course = res;
      });
    }

    this.getGroup(id).subscribe((res: Course) => {
      //TODO: HANDLE THE EMPTY GROUP BETTER
      console.log(res);
      if (res.hasOwnProperty('status')) {
        this.group = [];
      } else {
        this.group = res;
      }
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

  openModal(): void {
    const modalRef = this.modalService.open(FileUploadModalComponent);
    modalRef.componentInstance.name = 'fileUpload';
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

  joinGroup(): void {
    console.log('join group');
  }
}
