import { Component, OnInit } from '@angular/core';
import { ActivatedRoute, NavigationEnd, Router } from '@angular/router';
import { Assignment } from 'src/app/models/courses';
import { CourseService } from 'src/app/services/course-service.service';

@Component({
  selector: 'app-assignments',
  templateUrl: './assignments.component.html',
  styleUrls: ['./assignments.component.scss'],
})
export class AssignmentsComponent implements OnInit {
  assignments: any;

  constructor(
    private route: ActivatedRoute,
    private courseService: CourseService
  ) {}

  ngOnInit() {
    const id = parseInt(this.route.snapshot.paramMap?.get('id') || '', 10);
    if (!isNaN(id)) {
      this.courseService.getCourse(id).subscribe((res) => {
        this.assignments = res;
      });
    }
  }
}
