import { Component } from '@angular/core';
import { TestApiService } from './test.service';
@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.css'],
})
export class AppComponent {
  constructor(private testService: TestApiService) {}

  onClick() {
    this.testService.testGET().subscribe((res) => {
      console.log(res);
    });
  }
}
