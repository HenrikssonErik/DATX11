import { Component } from '@angular/core';
import { TooltipEnablerService } from 'src/app/services/tooltip-enabler.service';

@Component({
  selector: 'app-create-course',
  templateUrl: './create-course.component.html',
  styleUrls: ['./create-course.component.scss'],
})
export class CreateCourseComponent {
  formData = {
    name: '',
    abbreviation: '',
    groups: null,
    lp: null,
    year: this.minYear(),
  };

  constructor(private tooltipEnabler: TooltipEnablerService) {}

  ngOnInit(): void {
    this.enableTooltips();
  }

  private enableTooltips(): void {
    this.tooltipEnabler.enableTooltip();
  }

  onSubmit() {
    // Handle form submission
    console.log('onSubmit');
    console.log(this.formData);
  }

  minYear(): number {
    return new Date().getFullYear();
  }
}
