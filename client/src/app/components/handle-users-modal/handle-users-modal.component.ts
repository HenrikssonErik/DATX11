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
import Fuse from 'fuse.js';

@Component({
  selector: 'app-handle-users-modal',
  templateUrl: './handle-users-modal.component.html',
  styleUrls: ['./handle-users-modal.component.scss'],
})
export class HandleUsersModalComponent {
  @Input() users!: User[];
  @Input() course!: Course;
  usersList: User[] = [];
  csvData: string[] = [];
  newCid: string = '';
  searchString: string = '';
  isLoading: boolean = false;

  constructor(
    public activeModal: NgbActiveModal,
    private formBuilder: FormBuilder,
    private http: HttpClient,
    private toastr: ToastrService,
    private user_service: UserService,
    private toastrResponse: ToastrResponseService
  ) {}

  ngOnInit(): void {
    this.isLoading = true;
    this.user_service.getUsersInCourse(this.course.courseID).subscribe(
      (res: User[]) => {
        this.users = res;
        this.usersList = this.users;
        this.isLoading = false;
      },
      (error) => {
        console.error(error);
      }
    );
  }

  updateUsers() {
    this.user_service.getUsersInCourse(this.course.courseID).subscribe(
      (res: User[]) => {
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
    reader.onload = () => {
      const text = reader.result as string;
      this.csvData = text.split('\r\n');
    };
    reader.readAsText(file!);
  }

  submitCSV(): void {
    const headers = new HttpHeaders()
      .append('Cookies', document.cookie)
      .set('Cache-Control', 'public, max-age=3600');

    const formData = {
      Course: this.course.courseID,
      Cids: this.csvData,
    };

    this.http
      .post<HttpResponse<any>>(`${API_URL}/batchAddToCourse`, formData, {
        observe: 'response',
        headers: headers,
      })
      .subscribe({
        next: (response: any) => {
          try {
            if (response.status == 200) {
              this.toastr.success('Users added', response.body);
              this.csvData = [];
              this.newCid = '';
              this.updateUsers();
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

  submitCid(): void {
    this.csvData = [this.newCid];
    this.submitCSV();
  }

  updateRole(user: User): void {
    const headers = new HttpHeaders()
      .append('Cookies', document.cookie)
      .set('Cache-Control', 'public, max-age=3600');

    const formData = {
      Course: this.course.courseID,
      User: user.id,
      Role: user.role,
    };

    this.http
      .post<HttpResponse<any>>(`${API_URL}/changeUserRole`, formData, {
        observe: 'response',
        headers: headers,
      })
      .subscribe({
        next: (response: any) => {
          try {
            if (response.status == 200) {
              this.toastr.success(
                'Changed role for:' + user.fullname + ' Role:' + user.role,
                response.body
              );
              const index: number = this.users.indexOf(user);
              this.users.splice(index, 1);
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

  removeUser(user: User): void {
    const headers = new HttpHeaders()
      .append('Cookies', document.cookie)
      .set('Cache-Control', 'public, max-age=3600');

    const formData = {
      Course: this.course.courseID,
      User: user.id,
    };

    this.http
      .post<HttpResponse<any>>(`${API_URL}/removeFromCourse`, formData, {
        observe: 'response',
        headers: headers,
      })
      .subscribe({
        next: (response: any) => {
          try {
            if (response.status == 200) {
              this.toastr.success(
                'Removed' + user.fullname + ' Cid:' + user.cid,
                response.body
              );
              const index: number = this.users.indexOf(user);
              this.users.splice(index, 1);
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

  search() {
    const options = {
      keys: ['cid', 'email', 'fullname'],
      threshold: 0.3, // Adjust this value to control the "fuzziness" of the search
      ignoreLocation: true,
      includeScore: true,
    };
    console.log(this.searchString);

    if (this.searchString == '') {
      this.usersList = this.users;
    } else {
      const fuse = new Fuse(this.users, options);
      const result = fuse.search(this.searchString);
      this.usersList = result.map((r) => r.item);
    }
  }
}
