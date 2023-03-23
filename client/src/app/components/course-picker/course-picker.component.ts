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

  onCourseDrop(event: CdkDragDrop<Course[]>) {
    moveItemInArray(
      event.container.data,
      event.previousIndex,
      event.currentIndex
    );
  }

  onCourseDragStarted() {
    console.log('Course drag started');
  }

  onCourseDragEnded() {
    console.log('Course drag ended');
  }
}
