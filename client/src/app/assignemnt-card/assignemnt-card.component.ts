import { Component, ElementRef, Input } from '@angular/core';
import { FormControl, FormGroup } from '@angular/forms';
import { CourseService } from '../services/course-service.service';
import { ToastrService } from 'ngx-toastr';
import { Assignment } from '../models/courses';

@Component({
  selector: 'app-assignemnt-card',
  templateUrl: './assignemnt-card.component.html',
  styleUrls: ['./assignemnt-card.component.scss'],
})
export class AssignemntCardComponent {
  Files: File[] = [];
  fileDropEl!: ElementRef;
  allowedFileTypes = ['text/x-python', 'application/pdf', 'text/plain'];
  formatedDate!: string;

  form: FormGroup = new FormGroup({
    editMode: new FormControl(false),
    AssignmentName: new FormControl({ value: '', disabled: true }),
    Date: new FormControl({ value: new Date(), disabled: true }),
    Description: new FormControl({ value: '', disabled: true }),
  });

  @Input() courseID!: number;
  @Input() Assignment!: Assignment;

  constructor(
    private courseService: CourseService,
    private toastr: ToastrService
  ) {}

  ngOnInit() {
    this.form.get('AssignmentName')?.setValue(this.Assignment.Name);
    this.formatedDate = this.formatDate(this.Assignment.DueDate);

    this.form.get('Date')?.setValue(this.formatedDate);
    this.form.get('Description')?.setValue(this.Assignment.Description);
  }

  formatDate(dateObj: Date): string {
    const date = new Date(dateObj);
    const year = date.getFullYear().toString();
    const month = date.getMonth().toString().padStart(2, '0');
    const day = date.getDate().toString().padStart(2, '0');
    return `${year}-${month}-${day}`;
  }
  editToggle() {
    this.form.get('AssignmentName')?.enable();
    this.form.get('Description')?.enable();
    this.form.get('Date')?.enable();
    this.form.get('Files')?.enable();
  }

  fileBrowseHandler(files: Event): void {
    let fileInput: HTMLInputElement = files.target as HTMLInputElement;
    let fileList: FileList | null = fileInput.files;
    if (fileList) {
      this.prepareFilesList(Array.from(fileList));
    }
  }

  prepareFilesList(files: Array<File>): void {
    const allowedTypes = this.allowedFileTypes;
    for (const file of files) {
      const index = this.Files.findIndex((f) => f.name === file.name);
      if (allowedTypes.includes(file.type)) {
        if (index !== -1) {
          this.Files[index] = file;
          this.toastr.info(file.name + ' was replaced', 'Duplicate file', {
            closeButton: true,
          });
        } else {
          this.Files.push(file);
        }
      } else {
        this.toastr.warning(
          file.type + ' is not supported',
          'Unsupported file type',
          {
            closeButton: true,
          }
        );
      }
    }
    this.fileDropEl.nativeElement.value = '';
  }

  onSubmit() {
    const fileData = new FormData();
    this.Files.forEach((file: File): void =>
      fileData.append('files', file, file.name)
    );
    if (this.Files.length > 0) {
      console.log(fileData.get('files'));
      //make call here,change how unittest files works
    }
    if (this.form.get('AssignmentName')?.value != this.Assignment.Name) {
      console.log(this.form.get('AssignmentName')?.value);
      //make call here, create endpoint
    }
    if (this.form.get('Description')?.value != this.Assignment.Description) {
      console.log(this.form.get('Description')?.value);
      //make call here
    }
    if (this.form.get('Date')?.value != this.formatedDate) {
      console.log(typeof this.Assignment.DueDate);
      console.log(this.form.get('Date')?.value);
      //make call here
    }
  }

  changeDesc() {}
  changeName() {}
  changeDate() {}

  changeTests() {}
}
