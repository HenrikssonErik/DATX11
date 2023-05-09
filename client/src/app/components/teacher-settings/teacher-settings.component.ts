import { HttpClient, HttpHeaders, HttpResponse } from '@angular/common/http';
import { Component } from '@angular/core';
import { FormControl, FormGroup } from '@angular/forms';
import { ActivatedRoute } from '@angular/router';
import { NgbModal, NgbActiveModal } from '@ng-bootstrap/ng-bootstrap';
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
  id!: any;
  loadingAssignments: boolean = false;

  constructor(
    private courseService: CourseService,
    private route: ActivatedRoute,
    private toastr: ToastrService,
    private modalService: NgbModal
  ) {}

  ngOnInit(): void {
    this.id = parseInt(this.route.snapshot.paramMap?.get('id') || '', 10);
    if (!isNaN(this.id)) {
      this.updateCourse();
    }
  }

  updateCourse() {
    this.courseService.getCourse(this.id).subscribe((res: Course) => {
      this.course = res;
      this.form.get('Name')?.setValue(this.course.CourseName);
      this.form.get('Course')?.setValue(this.course.Course);
      this.sortAssignments();
    });
  }

  sortAssignments() {
    this.course.Assignments.sort((a, b) => a.AssignmentNr - b.AssignmentNr);
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

    modalRef.result.then(
      (result) => {
        console.log('Modal closed with result:', result);
        this.updateCourse();
        // Do something with the result
      },
      (reason) => {
        console.log('Modal dismissed with reason:', reason);
        // Handle the modal being dismissed (e.g. user clicked outside of the modal)
      }
    );
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
