import { Component, Input, OnInit } from '@angular/core';
import { Course } from 'src/app/models/courses';
import { CourseService } from 'src/app/services/course-service.service';
@Component({
  selector: 'app-course-picker',
  templateUrl: './course-picker.component.html',
  styleUrls: ['./course-picker.component.scss'],
})
export class CoursePickerComponent implements OnInit {
  courses: Course[] = [];
  currentCourses: Course[] = [];
  passedCourses: Course[] = [];

  constructor(private courseService: CourseService) {}

  ngOnInit(): void {
    //TODO: FIX so that we dont have to call this twice. Once here and once in courses.component.ts
    this.courseService.getCourses().subscribe((res: Course[]) => {
      this.courses = res;
      this.sortCourses();
    });
  }

  sortCourses() {
    const now = new Date();

    for (const course of this.courses) {
      // Check if all assignments in the course have due dates in the past
      const allAssignmentsPassed = course.Assignments.every(
        (assignment) => new Date(assignment.DueDate) < now
      );

      if (allAssignmentsPassed) {
        this.passedCourses.push(course);
      } else {
        this.currentCourses.push(course);
      }
    }
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
