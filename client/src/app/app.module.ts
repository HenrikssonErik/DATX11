import { NgModule } from '@angular/core';
import { BrowserModule } from '@angular/platform-browser';
import { HttpClientModule } from '@angular/common/http';
import { AppRoutingModule } from './app-routing.module';
import { AppComponent } from './app.component';
import { TestApiService } from './test.service';
import { FileUploadComponent } from './components/file-upload/file-upload.component';
import { DndDirective } from './directives/dnd.directive';
import { FormsModule } from '@angular/forms';

@NgModule({
  declarations: [AppComponent, FileUploadComponent, DndDirective],
  imports: [BrowserModule, AppRoutingModule, HttpClientModule, FormsModule],
  providers: [TestApiService], //should be replaced with the real deal later
  bootstrap: [AppComponent],
})
export class AppModule {}
