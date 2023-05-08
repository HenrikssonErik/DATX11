import { NgModule } from '@angular/core';
import { BrowserModule } from '@angular/platform-browser';
import {
  HttpClient,
  HttpClientModule,
  HTTP_INTERCEPTORS,
} from '@angular/common/http';
import { AppRoutingModule } from './app-routing.module';
import { AppComponent } from './app.component';
import { FileUploadComponent } from './components/file-upload/file-upload.component';
import { DndDirective } from './directives/dnd.directive';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';
import { ToastrModule } from 'ngx-toastr';
import { BrowserAnimationsModule } from '@angular/platform-browser/animations';
import { CommonModule } from '@angular/common';
import { NavbarComponent } from './components/navbar/navbar.component';
import { FooterComponent } from './components/footer/footer.component';
import { TestFeedbackComponent } from './components/test-feedback/test-feedback.component';
import { TestFeedbackCardComponent } from './components/test-feedback-card/test-feedback-card.component';
import { SpinnerComponent } from './components/spinner/spinner.component';
import { LoadingInterceptor } from './interceptors/loading.interceptor';
import { LoginComponent } from './components/login/login.component';
import { TranslateLoader, TranslateModule } from '@ngx-translate/core';
import { TranslateHttpLoader } from '@ngx-translate/http-loader';
import { HomePageComponent } from './components/home-page/home-page.component';
import { PageNotFoundComponent } from './components/page-not-found/page-not-found.component';
import { CoursesComponent } from './components/courses/courses.component';
import { MatTabsModule } from '@angular/material/tabs';
import { CourseComponent } from './components/course/course.component';
import { CoursePickerComponent } from './components/course-picker/course-picker.component';
import { AssignmentsComponent } from './components/assignments/assignments.component';
import { CreateCourseComponent } from './components/create-course/create-course.component';
import { VerifyEmailComponent } from './components/verify-email/verify-email.component';
import { FileUploadModalComponent } from './components/file-upload-modal/file-upload-modal.component';
import { NgbModule } from '@ng-bootstrap/ng-bootstrap';
import { TeacherSettingsComponent } from './components/teacher-settings/teacher-settings.component';
import { CreateAssignmentModalComponent } from './components/create-assignment-modal/create-assignment-modal.component';
import { HandleUsersModalComponent } from './components/handle-users-modal/handle-users-modal.component';
import { AssignmentCardComponent } from './components/assignment-card/assignment-card.component';
import { SubmissionsComponent } from './components/submissions/submissions.component';
import { GradingComponent } from './components/gradeing/grading.component';
import { FeedbackTeacherViewModalComponent } from './components/feedback-teacher-view-modal/feedback-teacher-view-modal.component';
import { ForgotPwdComponent } from './components/forgot-pwd/forgot-pwd.component';


export function HttpLoaderFactory(http: HttpClient) {
  return new TranslateHttpLoader(http, './assets/translations/', '.json');
}

@NgModule({
  declarations: [
    AppComponent,
    FileUploadComponent,
    DndDirective,
    NavbarComponent,
    FooterComponent,
    TestFeedbackComponent,
    TestFeedbackCardComponent,
    SpinnerComponent,
    LoginComponent,
    HomePageComponent,
    PageNotFoundComponent,
    CoursesComponent,
    CourseComponent,
    CoursePickerComponent,
    AssignmentsComponent,
    CreateCourseComponent,
    VerifyEmailComponent,
    FileUploadModalComponent,
    TeacherSettingsComponent,
    CreateAssignmentModalComponent,
    HandleUsersModalComponent,
    AssignmentCardComponent,
    SubmissionsComponent,
    GradingComponent,
    FeedbackTeacherViewModalComponent,
    ForgotPwdComponent,
  ],
  imports: [
    BrowserModule,
    AppRoutingModule,
    HttpClientModule,
    FormsModule,
    CommonModule,
    BrowserAnimationsModule,
    ToastrModule.forRoot(),
    ReactiveFormsModule,
    MatTabsModule,
    NgbModule,
    TranslateModule.forRoot({
      loader: {
        provide: TranslateLoader,
        useFactory: HttpLoaderFactory,
        deps: [HttpClient],
      },
    }),
  ],
  exports: [MatTabsModule],
  providers: [
    {
      provide: HTTP_INTERCEPTORS,
      useClass: LoadingInterceptor,
      multi: true,
    },
  ],
  bootstrap: [AppComponent],
})
export class AppModule {}
