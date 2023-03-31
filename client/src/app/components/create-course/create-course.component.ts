import { Component } from '@angular/core';

@Component({
  selector: 'app-create-course',
  templateUrl: './create-course.component.html',
  styleUrls: ['./create-course.component.scss'],
})
export class CreateCourseComponent {
  formData = {
    name: '',
    abbreviation: '',
    groups: null,
    lp: null,
    year: this.minYear(),
  };

  onSubmit() {
    // Handle form submission
    console.log('onSubmit');
    console.log(this.formData);
  }

  minYear(): number {
    return new Date().getFullYear();
  }
}
