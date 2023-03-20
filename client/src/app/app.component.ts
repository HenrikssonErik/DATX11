import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Component, OnInit } from '@angular/core';
import { UploadFileConfigService } from './services/upload-test-file-config.service';
import { UploadUnitTestConfigService } from './services/upload-unit-test-config.service';
import { API_URL } from 'src/environments/environment';
import { TranslationService } from './services/translation.service';

@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.css'],
})
export class AppComponent implements OnInit {
  constructor(
    public uploadTestFile: UploadFileConfigService,
    public uploadUnitTestFile: UploadUnitTestConfigService,
    private http: HttpClient,
    private translationService: TranslationService
  ) {}

  ngOnInit(): void {
    const language: string = this.translationService.getLanguage();
    this.translationService.setLanguage(language);
  }

  getTemplateFile() {
    // TODO: Temporarily do a get request here and retrieve the file.
  }

  //downloads a assignment file from the specified course and group.
  getfile(): void {
    this.http
      .post(
        `${API_URL}/getAssignmentFile`,

        // replace fixed values with dynamic user input, when that is implemented
        { groupId: 1, course: 6, assignment: 6, filename: 'Test1.pdf' },
        {
          observe: 'response',
          responseType: 'blob',
        }
      )
      .subscribe({
        next: (response) => {
          const contentDispositionHeader = response.headers.getAll(
            'Content-Disposition'
          )![0];
          const filename = contentDispositionHeader
            .split(';')[1]
            .split('=')[1]
            .replace(/"/g, '')
            .trim();
          var file = new File([response.body!], 'assignment');

          const url = URL.createObjectURL(file);
          const link = document.createElement('a');
          link.href = url;
          link.download = filename;
          link.click();
        },
        error: (err) => {
          //TODO: Handle the error
        },
      });
  }
}
