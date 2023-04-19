import { Component } from '@angular/core';
import { FormControl, FormGroup } from '@angular/forms';

@Component({
  selector: 'app-assignemnt-card',
  templateUrl: './assignemnt-card.component.html',
  styleUrls: ['./assignemnt-card.component.scss'],
})
export class AssignemntCardComponent {
  form: FormGroup = new FormGroup({
    editMode: new FormControl(false),
    //Name: new FormControl({ value: '', disabled: true }),
    //Course: new FormControl({ value: '', disabled: true }),
  });
}
