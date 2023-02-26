import { NgModule } from '@angular/core';
import { BrowserModule } from '@angular/platform-browser';
import { HttpClientModule, HTTP_INTERCEPTORS } from '@angular/common/http';
import { AppRoutingModule } from './app-routing.module';
import { AppComponent } from './app.component';
import { TestApiService } from './test.service';
import { FileUploadComponent } from './components/file-upload/file-upload.component';
import { DndDirective } from './directives/dnd.directive';
import { FormsModule } from '@angular/forms';
import { ToastrModule } from 'ngx-toastr';
import { BrowserAnimationsModule } from '@angular/platform-browser/animations';
import { CommonModule } from '@angular/common';
import { NavbarComponent } from './components/navbar/navbar.component';
import { FooterComponent } from './components/footer/footer.component';
import { TestFeedbackComponent } from './components/test-feedback/test-feedback.component';
import { TestFeedbackCardComponent } from './components/test-feedback-card/test-feedback-card.component';
import { SpinnerComponent } from './components/spinner/spinner.component';
import { LoadingInterceptor } from './interceptors/loading.interceptor';

@NgModule({
  declarations: [AppComponent, FileUploadComponent, DndDirective, NavbarComponent, FooterComponent, TestFeedbackComponent, TestFeedbackCardComponent, SpinnerComponent],
  imports: [BrowserModule, AppRoutingModule, HttpClientModule, FormsModule, CommonModule, BrowserAnimationsModule, ToastrModule.forRoot()],
  providers: [
    {
      provide: HTTP_INTERCEPTORS, useClass: LoadingInterceptor, multi: true
    }
  ], 
  bootstrap: [AppComponent],
})
export class AppModule {}
