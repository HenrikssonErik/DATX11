import { Component, Input, OnInit } from '@angular/core';

@Component({
  selector: 'app-test-feedback-card',
  templateUrl: './test-feedback-card.component.html',
  styleUrls: ['./test-feedback-card.component.scss']
})
export class TestFeedbackCardComponent implements OnInit {
  @Input() testFeedback: {
    fileStatus: string;
    fileName: string;
    testResponse: string;
  } | undefined;
  @Input() index: number = 0;

  constructor() { }

  ngOnInit(): void {
  }

  openFeedBackModal() {
    alert("Här tänkte jag kanske att man kunde öppna en modal med mer info???");
  }
}
