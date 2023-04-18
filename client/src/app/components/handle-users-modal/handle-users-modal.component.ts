import { HttpClient, HttpHeaders, HttpResponse } from '@angular/common/http';
import { Component, ElementRef, Input } from '@angular/core';
import { FormArray, FormBuilder, FormGroup, Validators } from '@angular/forms';
import { NgbActiveModal } from '@ng-bootstrap/ng-bootstrap';
import { ToastrService } from 'ngx-toastr';
import { Course } from 'src/app/models/courses';
import { User } from 'src/app/models/user';
import { ToastrResponseService } from 'src/app/services/toastr-response.service';
import { UserService } from 'src/app/services/user-service.service';
import { API_URL } from 'src/environments/environment';

@Component({
  selector: 'app-handle-users-modal',
  templateUrl: './handle-users-modal.component.html',
  styleUrls: ['./handle-users-modal.component.scss'],
})
export class HandleUsersModalComponent {
  @Input() users!: User[];
  @Input() course!: Course;
  csvData: string[] = [];

  constructor(
    public activeModal: NgbActiveModal,
    private formBuilder: FormBuilder,
    private http: HttpClient,
    private toastr: ToastrService,
    private user_service: UserService,
    private toastrResponse: ToastrResponseService
  ) {}

  ngOnInit(): void {
    this.user_service.getUsersInCourse(this.course.courseID).subscribe(
      (res: User[]) => {
        console.log(res);
        this.users = res;
      },
      (error) => {
        console.error(error);
      }
    );
  }

  handleFileInput(event: Event) {
    const files = (event.target as HTMLInputElement).files;
    const reader = new FileReader();
    const file = files!.item(0);
    console.log(file?.text);
    reader.onload = () => {
      const text = reader.result as string;
      this.csvData = text.split('\r\n');
    };
    reader.readAsText(file!);
  }

  createAssignment(): void {
    const headers = new HttpHeaders()
      .append('Cookies', document.cookie)
      .set('Cache-Control', 'public, max-age=3600');

    console.log(this.users);
  }

  submitCSV(): void {
    const headers = new HttpHeaders()
      .append('Cookies', document.cookie)
      .set('Cache-Control', 'public, max-age=3600');

    const formData = this.formBuilder.group({
      Course: this.course.courseID,
    });
    this.http
      .post<HttpResponse<any>>(`${API_URL}/createAssignment`, formData.value, {
        observe: 'response',
        headers: headers,
      })
      .subscribe({
        next: (response: any) => {
          try {
            if (response.status == 200) {
              this.toastr.success('Users Added', response.body);
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

  submitCid(): void {}
}
