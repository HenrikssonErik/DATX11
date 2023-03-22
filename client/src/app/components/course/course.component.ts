import { Component, Input, OnInit } from '@angular/core';
import { Course } from 'src/app/models/courses';

@Component({
  selector: 'app-course',
  templateUrl: './course.component.html',
  styleUrls: ['./course.component.scss'],
})
export class CourseComponent implements OnInit {
  @Input() data: Course | undefined;

  ngOnInit(): void {
    console.log(this.data);
  }
}
