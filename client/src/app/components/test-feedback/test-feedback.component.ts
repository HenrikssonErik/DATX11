import { Component, OnInit } from '@angular/core';

@Component({
  selector: 'app-test-feedback',
  templateUrl: './test-feedback.component.html',
  styleUrls: ['./test-feedback.component.scss'],
})
export class TestFeedbackComponent implements OnInit {
  feedbackFiles: {
    fileStatus: string;
    fileName: string;
    testResponse: string;
  }[] = [];

  constructor() {}

  ngOnInit(): void {
    /* Should (of course) be done dynamically in the future */
    this.feedbackFiles.push({
      fileStatus: 'warning',
      fileName: 'TestFile1',
      testResponse: 'Not following the PEP8 styling convention',
    });
  }
}
