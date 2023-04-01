import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Component, OnInit } from '@angular/core';
import { ActivatedRoute, NavigationEnd, Router } from '@angular/router';
import { Observable } from 'rxjs';
import { Assignment, Course } from 'src/app/models/courses';
import { CourseService } from 'src/app/services/course-service.service';
import { API_URL } from 'src/environments/environment';

@Component({
  selector: 'app-assignments',
  templateUrl: './assignments.component.html',
  styleUrls: ['./assignments.component.scss'],
})
export class AssignmentsComponent implements OnInit {
  course: Course = {} as Course;
  selectedTab: number = 0;

  constructor(
    private route: ActivatedRoute,
    private courseService: CourseService,
    private http: HttpClient
  ) {}

  ngOnInit() {
    const id = parseInt(this.route.snapshot.paramMap?.get('id') || '', 10);
    if (!isNaN(id)) {
      this.courseService.getCourse(id).subscribe((res: Course) => {
        this.course = res;
      });
    }

    this.getGroup().subscribe((res: Course) => {
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

  getGroup(): Observable<Course> {
    const headers = new HttpHeaders()
      .append('Cookies', document.cookie)
      .set('Cache-Control', 'public, max-age=3600');
    return this.http.get<Course>(`${API_URL}/getMyGroup`, {
      headers,
    });
  }

  formatDate(date: Date): string {
    return new Date(date).toLocaleDateString('sv-SE');
  }
}
