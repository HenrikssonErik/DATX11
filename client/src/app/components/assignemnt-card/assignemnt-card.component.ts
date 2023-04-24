import { Component, ElementRef, Input } from '@angular/core';
import { FormControl, FormGroup } from '@angular/forms';
import { CourseService } from '../../services/course-service.service';
import { ToastrService } from 'ngx-toastr';
import { Assignment } from '../../models/courses';
import { HttpClient, HttpHeaders, HttpResponse } from '@angular/common/http';
import { API_URL } from 'src/environments/environment';
import { ToastrResponseService } from 'src/app/services/toastr-response.service';

@Component({
  selector: 'app-assignemnt-card',
  templateUrl: './assignemnt-card.component.html',
  styleUrls: ['./assignemnt-card.component.scss'],
})
export class AssignemntCardComponent {
  Files: File[] = [];
  fileDropEl!: ElementRef;
  allowedFileTypes = ['text/x-python'];
  formatedDate!: string;

  headers = new HttpHeaders()
    .append('Cookies', document.cookie)
    .set('Cache-Control', 'public, max-age=3600');

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
    private toastr: ToastrService,
    private http: HttpClient,
    private toastrResponse: ToastrResponseService
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
    if (this.form.get('editMode')?.value) {
      this.form.get('AssignmentName')?.disable();
      this.form.get('Description')?.disable();
      this.form.get('Date')?.disable();
      this.form.get('Files')?.disable();
    } else {
      this.form.get('AssignmentName')?.enable();
      this.form.get('Description')?.enable();
      this.form.get('Date')?.enable();
      this.form.get('Files')?.enable();
    }
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
    if (this.Files.length > 0) {
      this.changeTests();
    }
    if (this.form.get('AssignmentName')?.value != this.Assignment.Name) {
      this.changeName();
    }
    if (this.form.get('Description')?.value != this.Assignment.Description) {
      this.changeDesc();
    }
    if (this.form.get('Date')?.value != this.formatedDate) {
      this.changeDate();
    }
  }

  changeDesc() {
    const formData = new FormData();
    formData.append('Desc', this.form.get('Description')?.value);
    formData.append('Course', this.courseID.toString());
    formData.append('Assignment', this.Assignment.AssignmentNr.toString());

    this.http
      .post<HttpResponse<any>>(`${API_URL}/editDescription`, formData, {
        observe: 'response',
        headers: this.headers,
      })
      .subscribe({
        next: (response: any) => {
          try {
            if (response.status == 200) {
              this.toastr.success('Description Updated', response.body);
            }
          } catch {
            throw new Error('unexpected_error');
          }
        },
        error: (err) => {
          let statusMsg: string = err.error.status;
          const [errorMessage, errorTitle]: string[] =
            this.toastrResponse.getToastrResponse(statusMsg);
          this.toastr.error(errorMessage, errorTitle, {
            closeButton: true,
          });
        },
      });
  }
  changeName() {
    const formData = new FormData();
    formData.append('Name', this.form.get('AssignmentName')?.value);
    formData.append('Course', this.courseID.toString());
    formData.append('Assignment', this.Assignment.AssignmentNr.toString());

    this.http
      .post<HttpResponse<any>>(`${API_URL}/editAssignmentName`, formData, {
        observe: 'response',
        headers: this.headers,
      })
      .subscribe({
        next: (response: any) => {
          try {
            if (response.status == 200) {
              this.toastr.success('Name Updated', response.body);
            }
          } catch {
            throw new Error('unexpected_error');
          }
        },
        error: (err) => {
          let statusMsg: string = err.error.status;
          const [errorMessage, errorTitle]: string[] =
            this.toastrResponse.getToastrResponse(statusMsg);
          this.toastr.error(errorMessage, errorTitle, {
            closeButton: true,
          });
        },
      });
  }

  changeDate() {
    const formData = new FormData();
    formData.append('Date', this.form.get('Date')?.value);
    formData.append('Course', this.courseID.toString());
    formData.append('Assignment', this.Assignment.AssignmentNr.toString());

    this.http
      .post<HttpResponse<any>>(`${API_URL}/changeAssignmentDate`, formData, {
        observe: 'response',
        headers: this.headers,
      })
      .subscribe({
        next: (response: any) => {
          try {
            if (response.status == 200) {
              this.toastr.success('Due Date Updated', response.body);
            }
          } catch {
            throw new Error('unexpected_error');
          }
        },
        error: (err) => {
          let statusMsg: string = err.error.status;
          const [errorMessage, errorTitle]: string[] =
            this.toastrResponse.getToastrResponse(statusMsg);
          this.toastr.error(errorMessage, errorTitle, {
            closeButton: true,
          });
        },
      });
  }

  changeTests() {
    const fileData = new FormData();
    this.Files.forEach((file: File): void =>
      fileData.append('files', file, file.name)
    );

    fileData.append('Course', this.courseID.toString());
    fileData.append('Assignment', this.Assignment.AssignmentNr.toString());
    this.http
      .post<HttpResponse<any>>(`${API_URL}/unitTest`, fileData, {
        observe: 'response',
        headers: this.headers,
      })
      .subscribe({
        next: (response: any) => {
          try {
            if (response.status == 200) {
              this.toastr.success('Unittests Updated', response.body);
              //location.reload();
            }
          } catch {
            throw new Error('unexpected_error');
          }
        },
        error: (err) => {
          let statusMsg: string = err.error.status;
          const [errorMessage, errorTitle]: string[] =
            this.toastrResponse.getToastrResponse(statusMsg);
          this.toastr.error(errorMessage, errorTitle, {
            closeButton: true,
          });
        },
      });
  }
}
