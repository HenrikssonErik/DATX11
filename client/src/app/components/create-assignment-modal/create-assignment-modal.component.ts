import { HttpClient, HttpHeaders, HttpResponse } from '@angular/common/http';
import { Component, ElementRef, Input, SimpleChanges } from '@angular/core';
import { FormArray, FormBuilder, FormGroup, Validators } from '@angular/forms';
import { NgbActiveModal } from '@ng-bootstrap/ng-bootstrap';
import { ToastrService } from 'ngx-toastr';
import { Course } from 'src/app/models/courses';
import { CourseService } from 'src/app/services/course-service.service';
import { ToastrResponseService } from 'src/app/services/toastr-response.service';
import { API_URL } from 'src/environments/environment';

@Component({
  selector: 'app-create-assignment-modal',
  templateUrl: './create-assignment-modal.component.html',
  styleUrls: ['./create-assignment-modal.component.scss'],
})
export class CreateAssignmentModalComponent {
  form!: FormGroup;
  @Input() course!: Course;
  fileControls: any;
  Files: File[] = [];
  fileDropEl!: ElementRef;
  allowedFileTypes = ['text/x-python', 'application/pdf', 'text/plain'];

  constructor(
    public activeModal: NgbActiveModal,
    private fb: FormBuilder,
    private formBuilder: FormBuilder,
    private http: HttpClient,
    private toastr: ToastrService,
    private toastrResponse: ToastrResponseService
  ) {}

  ngOnInit(): void {
    this.form = this.fb.group({
      AssignmentName: ['', Validators.required],
      Date: ['', Validators.required],
      Description: ['', Validators.required],
      MaxScore: [
        0,
        [
          Validators.required,
          Validators.min(1),
          Validators.min(this.form?.controls['PassScore'].value),
        ],
      ],
      PassScore: [0, [Validators.required, Validators.min(1)]],
      PassFail: [false],
      numOfFiles: [0, [Validators.required, Validators.min(1)]],
      fileNames: this.formBuilder.array(
        [],
        Validators.pattern(/(\.pdf|\.py|\.txt)$/)
      ),
      Course: this.course.courseID,
    });

    this.form.controls['numOfFiles'].valueChanges.subscribe((numFiles) => {
      this.fileControls = [];
      const fileArray = this.form.get('fileNames') as FormArray;
      fileArray.clear();
      for (let i = 0; i < numFiles; i++) {
        const control = this.formBuilder.control('');
        this.fileControls.push(control);
        fileArray.push(control);
      }
    });
  }

  passFailToggle() {
    if (this.form.get('PassFail')!.value) {
      this.form.controls['MaxScore']?.setValue(0);
      this.form.controls['PassScore']?.setValue(0);
    } else {
      this.form.controls['MaxScore']?.setValue(1);
      this.form.controls['PassScore']?.setValue(1);
    }
  }

  changeMinVal() {
    this.form.controls['MaxScore'].clearValidators();
    this.form.controls['MaxScore'].addValidators([
      Validators.required,
      Validators.min(this.form?.controls['PassScore'].value),
    ]);
    this.form.controls['MaxScore'].updateValueAndValidity();
    console.log(this.form.controls['MaxScore'].valid);
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

  createAssignment(): void {
    const headers = new HttpHeaders()
      .append('Cookies', document.cookie)
      .set('Cache-Control', 'public, max-age=3600');
    console.log('create');
    const formData = { ...this.form };
    delete formData.value.numOfFiles;
    const fileData = new FormData();
    this.Files.forEach((file: File): void =>
      fileData.append('files', file, file.name)
    );

    this.http
      .post<HttpResponse<any>>(`${API_URL}/createAssignment`, formData.value, {
        observe: 'response',
        headers: headers,
      })
      .subscribe({
        next: (response: any) => {
          try {
            if (response.status == 200) {
              this.toastr.success('Assignment Created', response.body);
              this.postUnittests(fileData, headers);
              //location.reload();
            }
          } catch {
            throw new Error('unexpected_error');
          }
        },
        error: (err) => {
          let statusMsg: string = err.error.status;
          const [errorMessage, errorTitle]: string[] =
            this.toastrResponse.getToastrRepsonse(statusMsg);
          this.toastr.error(errorMessage, errorTitle, {
            closeButton: true,
          });
        },
      });
  }

  postUnittests(fileData: FormData, headers: HttpHeaders) {
    //add course and assignment to formdata,
    //could mb work as assignemtn nr: this.course.Assignments.length+1
    fileData.append('Course', this.course.courseID.toString());
    fileData.append(
      'Assignment',
      (this.course.Assignments.length + 1).toString()
    );
    this.http
      .post<HttpResponse<any>>(`${API_URL}/unitTest`, fileData, {
        observe: 'response',
        headers: headers,
      })
      .subscribe({
        next: (response: any) => {
          try {
            if (response.status == 200) {
              this.toastr.success('Unittests added', response.body);
              location.reload();
            }
          } catch {
            throw new Error('unexpected_error');
          }
        },
        error: (err) => {
          let statusMsg: string = err.error.status;
          const [errorMessage, errorTitle]: string[] =
            this.toastrResponse.getToastrRepsonse(statusMsg);
          this.toastr.error(errorMessage, errorTitle, {
            closeButton: true,
          });
        },
      });
  }
}
