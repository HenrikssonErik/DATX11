import { Component, OnInit } from '@angular/core';

@Component({
  selector: 'app-test-feedback',
  templateUrl: './test-feedback.component.html',
  styleUrls: ['./test-feedback.component.scss']
})
export class TestFeedbackComponent implements OnInit {

  constructor() { }

  ngOnInit(): void {
  }

  openFeedBackModal() {
    alert("Här tänkte jag kanske att man kunde öppna en modal med mer info???");
  }

}
