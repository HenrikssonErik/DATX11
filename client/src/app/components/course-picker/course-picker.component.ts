import { Component, Input, OnInit } from '@angular/core';
import { ActivatedRoute, NavigationEnd, Router } from '@angular/router';
import { Assignment, Course } from 'src/app/models/courses';
import { Location } from '@angular/common';
import { CourseService } from 'src/app/services/course-service.service';
@Component({
  selector: 'app-course-picker',
  templateUrl: './course-picker.component.html',
  styleUrls: ['./course-picker.component.scss'],
})
export class CoursePickerComponent implements OnInit {
  courses: Course[] = [];

  constructor(private router: Router, private courseService: CourseService) {}

  ngOnInit(): void {
    //TODO: FIX so that we dont have to call this twice. Once here and once in courses.component.ts
    this.courseService.getCourses().subscribe((res: Course[]) => {
      this.courses = res;
    });
  }

  goToCourse(id: number) {
    this.router.navigate([`courses/${id}`]);
  }

  isTeacher(): boolean {
    if (
      document.cookie.includes('Teacher') ||
      document.cookie.includes('Admin')
    ) {
      return true;
    } else return false;
  }
}
