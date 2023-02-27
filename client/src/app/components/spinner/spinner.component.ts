import { Component, OnInit } from '@angular/core';
import { LoadingspinnerService } from 'src/app/services/loadingspinner.service';

@Component({
  selector: 'app-spinner',
  templateUrl: './spinner.component.html',
  styleUrls: ['./spinner.component.scss']
})
export class SpinnerComponent implements OnInit {

  constructor(public spinner : LoadingspinnerService) { }

  ngOnInit(): void {
  }

}
