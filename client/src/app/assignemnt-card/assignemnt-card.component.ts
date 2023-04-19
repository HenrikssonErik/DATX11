import { Component } from '@angular/core';
import { FormGroup } from '@angular/forms';

@Component({
  selector: 'app-assignemnt-card',
  templateUrl: './assignemnt-card.component.html',
  styleUrls: ['./assignemnt-card.component.scss'],
})
export class AssignemntCardComponent {
  form!: FormGroup;
}
