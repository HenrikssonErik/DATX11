import { Component, Input } from '@angular/core';
import { NgbActiveModal } from '@ng-bootstrap/ng-bootstrap';
import { TestResult } from 'src/app/models/submission';
import { SubmissionService } from 'src/app/services/submission.service';

@Component({
  selector: 'app-feedback-teacher-view-modal',
  templateUrl: './feedback-teacher-view-modal.component.html',
  styleUrls: ['./feedback-teacher-view-modal.component.scss'],
})
export class FeedbackTeacherViewModalComponent {
  @Input() assignmentNr!: number;
  @Input() courseId!: number;
  @Input() groupId!: number;
  @Input() groupNumber!: number;
  submission!: TestResult[];
  isLoading: boolean = false;

  constructor(
    private submissionService: SubmissionService,
    public activeModal: NgbActiveModal
  ) {}

  ngOnInit(): void {
    this.isLoading = true;
    this.submissionService
      .getTestingFeedback(this.courseId, this.assignmentNr, this.groupId)
      .subscribe({
        next: (data: any) => {
          //console.log(data);
          this.submission = data;
          console.log('submissions:', this.submission);
        },
        error: (error) => {
          this.isLoading = false;
          console.error('Failed to get data:', error);
        },
        complete: () => {
          this.isLoading = false;
          console.log('complete');
        },
      });
  }

  parseGeneralTest(str: string): any[] {
    let errors: any[] = [];
    const lines = str.split('\n');

    for (const line of lines) {
      const matches = line.match(/(.+):(\d+):(\d+):\s*(\w+)\s*(.*)/);
      if (matches) {
        const [, filePath, lineNum, colNum, errorCode, message] = matches;
        const error: any = {
          filePath,
          lineNum: parseInt(lineNum),
          colNum: parseInt(colNum),
          errorCode,
          message,
        };
        errors.push(error);
      }
    }
    return errors;
  }

  parseUnitTest(header: string, content: string): any {
    const headerRegex = /^.*_(\d+)\.(\w+)\.(\w+)$/;
    const headerMatch = header.match(headerRegex);
    let parsedUnitTest = {};
    let testNumber = '';
    let testClass = '';
    let test = '';
    if (headerMatch) {
      testNumber = headerMatch[1];
      testClass = headerMatch[2];
      test = headerMatch[3];
    }

    const error = content.substring(content.indexOf(test) + test.length + 1);

    parsedUnitTest = {
      testNumber: testNumber,
      testClass: testClass,
      test: test,
      error: error,
    };
    return [parsedUnitTest];
  }

  parseErrors(str: string): string {
    const error: string = str.substring(str.lastIndexOf(',') + 1);
    return error;
  }
}
