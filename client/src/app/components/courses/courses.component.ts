import { Component, OnInit } from '@angular/core';
import { Course, Courses } from 'src/app/models/courses';
import { User } from 'src/app/models/user';
import { CourseService } from 'src/app/services/course-service.service';
import { UserService } from 'src/app/services/user-service.service';

class Deadline {
  Course!: string;
  Date!: string;

  constructor(course: string, date: Date) {
    this.Course = course;
    console.log(typeof date);
    this.Date = date.toISOString().substring(0, 10);
  }
}

@Component({
  selector: 'app-courses',
  templateUrl: './courses.component.html',
  styleUrls: ['./courses.component.scss'],
})
export class CoursesComponent implements OnInit {
  courses: Course[] = [];
  events = [];
  deadlines: Deadline[] = [];
  labs: number = 0;
  user: User = {
    cid: '',
    email: '',
    fullname: '',
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
      this.populateDashboard();
      //console.log(this.courses);
    });
  }

  populateDashboard(): void {
    var tempLabs = 0;
    var tempDeadlines: Deadline[] = [];

    for (var i = 0; i < this.courses.length; i++) {
      tempLabs = tempLabs + this.courses[i].Assignments.length;
      tempDeadlines = tempDeadlines.concat(
        this.findUpcomingAssignments(
          this.courses[i].Assignments,
          this.courses[i].Course
        )
      );
    }

    this.labs = tempLabs;
    this.deadlines = tempDeadlines;
  }

  findUpcomingAssignments(assignments: any[], course: string): Deadline[] {
    const deadlines: Deadline[] = [];
    for (let i = 0; i < assignments.length; i++) {
      if (this.isDateUpcoming(assignments[i].DueDate)) {
        deadlines.push(new Deadline(course, new Date(assignments[i].DueDate)));
      }
    }
    return deadlines;
  }

  isDateUpcoming(date: Date): boolean {
    const now = new Date();
    now.setHours(0, 0, 0, 0); //to reset timeframes smaller than days
    // Check if the date is in the future
    if (new Date(date).getTime() >= now.getTime()) {
      return true;
    }
    return false;
  }
}
