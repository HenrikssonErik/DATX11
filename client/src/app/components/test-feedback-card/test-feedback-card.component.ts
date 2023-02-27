import { Component, Input, OnInit } from '@angular/core';

interface LintError{
  filePath: string;
  lineNum: number;
  colNum: number;
  errorCode: string;
  message: string;
};

@Component({
  selector: 'app-test-feedback-card',
  templateUrl: './test-feedback-card.component.html',
  styleUrls: ['./test-feedback-card.component.scss']
})
export class TestFeedbackCardComponent implements OnInit {
  /*@Input() testFeedback: {
    fileStatus: string;
    fileName: string;
    testResponse: string;
  } | undefined;*/
  @Input() file :any;

  constructor() { }

  ngOnInit(): void {

    this.parseLintErrors(this.file.fileContent)
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

    console.log(errors);
  
    return errors;
  }

  openFeedBackModal() {
    alert("Här tänkte jag kanske att man kunde öppna en modal med mer info???");
  }
}
