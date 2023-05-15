import { Component, Input } from '@angular/core';
import { SubmissionService } from 'src/app/services/submission.service';
import { TestResult } from 'src/app/models/submission';

@Component({
  selector: 'app-submissions',
  templateUrl: './submissions.component.html',
  styleUrls: ['./submissions.component.scss'],
})
export class SubmissionsComponent {
  @Input() assignmentNr!: number;
  @Input() courseId!: number;
  @Input() fileList!: string[];
  @Input() groupId?: number;
  submissions!: TestResult[];
  generalTest!: any[];
  isLoading: boolean = false;
  constructor(private submissionService: SubmissionService) {}

  ngOnInit(): void {
    this.getSubmissions();
  }

  getSubmissions() {
    this.isLoading = true;
    this.submissionService
      .getSubmission(this.courseId, this.assignmentNr)
      .subscribe({
        next: (res: TestResult[]) => {
          console.log('res');
          console.log(res);
          this.submissions = res;
          this.submissions.sort((a, b) => b.Submission - a.Submission);
        },
        error: (err) => {
          console.log(err);
          this.isLoading = false;
        },
        complete: () => {
          this.isLoading = false;
          console.log(this.submissions);
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

  downloadFile(fileName: string, submission: number) {
    this.submissionService.downloadSubmissionFile(
      this.courseId,
      this.groupId!,
      this.assignmentNr,
      submission,
      fileName
    );
  }

  parseSuccesses(str: any): string {
    const dotIndex = str.indexOf('.');
    if (dotIndex !== -1) {
      return str.substring(dotIndex + 1);
    }
    return 'Successfull test not found';
  }
}
