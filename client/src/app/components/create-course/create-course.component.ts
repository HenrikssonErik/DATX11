import { HttpClient, HttpHeaders, HttpResponse } from '@angular/common/http';
import { Component } from '@angular/core';
import { UntypedFormBuilder } from '@angular/forms';
import { ToastrService } from 'ngx-toastr';
import { ToastrResponseService } from 'src/app/services/toastr-response.service';
import { TooltipEnablerService } from 'src/app/services/tooltip-enabler.service';
import { API_URL } from 'src/environments/environment';
import { CourseService } from 'src/app/services/course-service.service';

@Component({
  selector: 'app-create-course',
  templateUrl: './create-course.component.html',
  styleUrls: ['./create-course.component.scss'],
})
export class CreateCourseComponent {
  formData = {
    Course: null,
    Abbreviation: null,
    TeachingPeriod: null,
    Year: this.minYear(),
  };

  constructor(
    private tooltipEnabler: TooltipEnablerService,
    private toastr: ToastrService,
    private toastrResponse: ToastrResponseService,
    private http: HttpClient,
    private courseService: CourseService
  ) {}

  ngOnInit(): void {
    this.enableTooltips();
  }

  private enableTooltips(): void {
    this.tooltipEnabler.enableTooltip();
  }

  onSubmit(): void {
    // Handle form submission

    const headers = new HttpHeaders()
      .append('Cookies', document.cookie)
      .set('Cache-Control', 'public, max-age=3600');

    this.http
      .post<HttpResponse<any>>(`${API_URL}/createCourse`, this.formData, {
        observe: 'response',
        headers: headers,
      })
      .subscribe({
        next: (response: any) => {
          try {
            if (response.status == 200) {
              this.toastr.success('', response.body);
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

  minYear(): number {
    return new Date().getFullYear();
  }
}
