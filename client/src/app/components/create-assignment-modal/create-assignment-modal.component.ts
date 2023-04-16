import { Component, Input, SimpleChanges } from '@angular/core';
import { FormArray, FormBuilder, FormGroup, Validators } from '@angular/forms';
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
  fileControls: any;

  constructor(
    public activeModal: NgbActiveModal,
    private fb: FormBuilder,
    private courseService: CourseService,
    private formBuilder: FormBuilder
  ) {}

  ngOnInit(): void {
    this.form = this.fb.group({
      AssignmentName: ['', Validators.required],
      dueDate: ['', Validators.required],
      description: ['', Validators.required],
      numOfFiles: [0, Validators.required],
      fileInput: [''],
      fileArray: this.formBuilder.array([]),
    });

    this.form.controls['numOfFiles'].valueChanges.subscribe((numFiles) => {
      this.fileControls = [];
      const fileArray = this.form.get('fileArray') as FormArray;
      fileArray.clear();
      for (let i = 0; i < numFiles; i++) {
        const control = this.formBuilder.control('');
        this.fileControls.push(control);
        fileArray.push(control);
      }
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

  getFiles() {
    const numFiles = this.form.controls['numOfFiles'].value;
    return Array.from({ length: numFiles }, (_, i) => i);
  }
}
