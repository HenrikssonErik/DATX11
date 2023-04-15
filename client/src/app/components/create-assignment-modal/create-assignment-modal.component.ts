import { Component, Input, SimpleChanges } from '@angular/core';
import { FormBuilder, FormGroup, Validators } from '@angular/forms';
import { NgbActiveModal } from '@ng-bootstrap/ng-bootstrap';
import { Course } from 'src/app/models/courses';
import { CourseService } from 'src/app/services/course-service.service';

@Component({
  selector: 'app-create-assignment-modal',
  templateUrl: './create-assignment-modal.component.html',
  styleUrls: ['./create-assignment-modal.component.scss'],
})
export class CreateAssignmentModalComponent {
  form!: FormGroup;
  @Input() course!: Course;
  numOfFiles: number = 0;
  numOfFilesArray: Number[] = [];

  constructor(
    public activeModal: NgbActiveModal,
    private fb: FormBuilder,
    private courseService: CourseService
  ) {}

  ngOnInit(): void {
    this.form = this.fb.group({
      AssignmentName: ['', Validators.required],
      dueDate: ['', Validators.required],
      description: ['', Validators.required],
      numOfFiles: [0, Validators.required],
    });
  }

  ngOnChanges(changes: SimpleChanges): void {
    if (changes['numOfFiles']) {
      console.log('hej');
      this.updateNumOfFilesArray();
    }
  }

  updateNumOfFilesArray(): void {
    this.numOfFilesArray = Array(this.numOfFiles)
      .fill(0)
      .map((x, i) => i);
  }

  createAssignment(): void {
    console.log(this.form.value);
  }
}
