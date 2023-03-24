import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { AppComponent } from './app.component';
import { CoursesComponent } from './components/courses/courses.component';
import { FileUploadComponent } from './components/file-upload/file-upload.component';
import { HomePageComponent } from './components/home-page/home-page.component';
import { LoginComponent } from './components/login/login.component';
import { PageNotFoundComponent } from './components/page-not-found/page-not-found.component';
import { AuthguardGuard } from './authguard.guard';
import { AssignmentsComponent } from './components/assignments/assignments.component';

const routes: Routes = [
  { path: '', component: HomePageComponent },
  { path: 'login', component: LoginComponent },
  {
    path: 'courses',
    component: CoursesComponent,
    canActivate: [AuthguardGuard],
    children: [{ path: ':id', component: AssignmentsComponent }],
  },
  { path: 'upload', component: FileUploadComponent },
  { path: '404', component: PageNotFoundComponent },
  { path: '**', redirectTo: '/404' },
];

@NgModule({
  imports: [RouterModule.forRoot(routes)],
  exports: [RouterModule],
})
export class AppRoutingModule {}
