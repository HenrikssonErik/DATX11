import { Component, Input, OnChanges, OnInit, SimpleChanges } from '@angular/core';

interface LintError{
  filePath: string;
  lineNum: number;
  colNum: number;
  errorCode: string;
  message: string;
};

@Component({
  selector: 'app-test-feedback',
  templateUrl: './test-feedback.component.html',
  styleUrls: ['./test-feedback.component.scss'],
})
export class TestFeedbackComponent implements OnInit {

  @Input() feedbackFiles: any;

  constructor() {}

  ngOnInit(): void {
  
    /* Should (of course) be done dynamically in the future */
 
  }

  
  parseLintErrors(str: string): LintError[] {
    
    const errors: LintError[] = [];
    const lines = str.split("\n");
  
    for (const line of lines) {
      const matches = line.match(
        /(.+):(\d+):(\d+):\s*(\w+)\s*(.*)/
      );
      if (matches) {
        const [, filePath, lineNum, colNum, errorCode, message] =
          matches;
        const error: LintError = {
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
}
