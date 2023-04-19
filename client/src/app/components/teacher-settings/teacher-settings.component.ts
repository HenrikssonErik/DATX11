import { HttpClient, HttpHeaders, HttpResponse } from '@angular/common/http';
import { Component } from '@angular/core';
import { FormControl, FormGroup } from '@angular/forms';
import { ActivatedRoute } from '@angular/router';
import { NgbModal } from '@ng-bootstrap/ng-bootstrap';
import { ToastrService } from 'ngx-toastr';
import { Course } from 'src/app/models/courses';
import { CourseService } from 'src/app/services/course-service.service';
import { API_URL } from 'src/environments/environment';
import { CreateAssignmentModalComponent } from '../create-assignment-modal/create-assignment-modal.component';
import { HandleUsersModalComponent } from '../handle-users-modal/handle-users-modal.component';

@Component({
  selector: 'app-teacher-settings',
  templateUrl: './teacher-settings.component.html',
  styleUrls: ['./teacher-settings.component.scss'],
})
export class TeacherSettingsComponent {
  form: FormGroup = new FormGroup({
    editMode: new FormControl(false),
    Name: new FormControl({ value: '', disabled: true }),
    Course: new FormControl({ value: '', disabled: true }),
  });
  course: Course = {} as Course;

  constructor(
    private courseService: CourseService,
    private route: ActivatedRoute,
    private toastr: ToastrService,
    private modalService: NgbModal
  ) {}

  ngOnInit(): void {
    const id = parseInt(this.route.snapshot.paramMap?.get('id') || '', 10);
    if (!isNaN(id)) {
      this.courseService.getCourse(id).subscribe((res: Course) => {
        this.course = res;
        this.form.get('Name')?.setValue(this.course.CourseName);
        this.form.get('Course')?.setValue(this.course.Course);
      });
    }
  }

  editToggle(): void {
    this.form.get('Name')?.setValue(this.course.CourseName);

    if (this.form.get('editMode')?.value) {
      this.form.get('Name')?.enable();
    } else {
      this.form.get('Name')?.disable();
    }
  }

  openCreateAssignmentModal(): void {
    const modalRef = this.modalService.open(CreateAssignmentModalComponent);
    modalRef.componentInstance.name = 'CreateAssignmentModal';
    modalRef.componentInstance.course = this.course;
  }

  openHandleUsersModal(): void {
    const modalRef = this.modalService.open(HandleUsersModalComponent);
    modalRef.componentInstance.name = 'HandleUsersModal';
    modalRef.componentInstance.course = this.course;
  }

  changeCourseName(): void {
    if (this.form.get('Name')?.value == this.course.CourseName) {
      return;
    } else {
      const newName = this.form.get('Name')?.value;
      this.courseService
        .changeCourseName(newName, this.course.courseID)
        .subscribe({
          next: (response: any) => {
            console.log(response);
            if (response.status == 200) {
              this.course.CourseName = this.form.get('Name')?.value;
              this.form.get('editMode')?.setValue(false);
            }
          },
          error: (error: any) => {
            this.toastr.error('', error.error);
          },
          complete() {
            console.log('complete');
          },
        });
    }
  }
}
