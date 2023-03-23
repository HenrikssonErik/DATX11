import { CdkDragDrop, moveItemInArray } from '@angular/cdk/drag-drop';
import { Component, Input } from '@angular/core';
import { Course } from 'src/app/models/courses';

@Component({
  selector: 'app-course-picker',
  templateUrl: './course-picker.component.html',
  styleUrls: ['./course-picker.component.scss'],
})
export class CoursePickerComponent {
  @Input() courses: Course[] = [];
  //TODO: Annoying to have to use !
  selectedCourse!: Course | undefined;

  constructor() {}

  setSelectedCourse(course: Course) {
    console.log(course);
    this.selectedCourse = course;
  }
  goBack() {
    this.selectedCourse = undefined;
  }
}
