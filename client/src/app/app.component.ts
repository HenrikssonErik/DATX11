import { Component } from '@angular/core';
import { UploadFileConfigService } from './services/upload-test-file-config.service';
import { UploadUnitTestConfigService } from './services/upload-unit-test-config.service';

@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.css'],
})
export class AppComponent {
  constructor(public uploadTestFile : UploadFileConfigService, public uploadUnitTestFile: UploadUnitTestConfigService) {}


  getTemplateFile() {
    // TODO: Temporarily do a get request here and retrieve the file.
  }


}
