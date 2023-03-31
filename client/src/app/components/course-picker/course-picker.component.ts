import { Component, Input, OnInit } from '@angular/core';
import { NavigationEnd, Router } from '@angular/router';
import { Assignment, Course } from 'src/app/models/courses';
import { Location } from '@angular/common';
@Component({
  selector: 'app-course-picker',
  templateUrl: './course-picker.component.html',
  styleUrls: ['./course-picker.component.scss'],
})
export class CoursePickerComponent implements OnInit {
  @Input() courses: Course[] = [];
  showCourses = true;

  constructor(private router: Router, private location: Location) {}

  ngOnInit(): void {
    //TODO: Don't like this.
    this.location.onUrlChange((url: string) => {
      if (url.endsWith('/courses') && !this.showCourses) {
        this.showCourses = true;
      }
    });
  }

  goToCourse(id: number) {
    this.showCourses = false;
    this.router.navigate(['/courses', id]);
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
