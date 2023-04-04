import { Component, OnInit } from '@angular/core';
import { Course, Courses } from 'src/app/models/courses';
import { User } from 'src/app/models/user';
import { CourseService } from 'src/app/services/course-service.service';
import { UserService } from 'src/app/services/user-service.service';

@Component({
  selector: 'app-courses',
  templateUrl: './courses.component.html',
  styleUrls: ['./courses.component.scss'],
})
export class CoursesComponent implements OnInit {
  courses: Course[] = [];
  events = [];
  deadlines = [];
  user: User = {
    cid: '',
    email: '',
  };

  constructor(
    private userService: UserService,
    private courseService: CourseService
  ) {}

  ngOnInit(): void {
    this.userService.getUserData().subscribe((res: User) => {
      this.user = res;
      //console.log(this.user);
    });

    this.courseService.getCourses().subscribe((res: Course[]) => {
      this.courses = res;
      //console.log(this.courses);
    });
  }
}
