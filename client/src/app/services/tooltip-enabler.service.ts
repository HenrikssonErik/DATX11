import { Injectable } from '@angular/core';

declare var bootstrap: any;

@Injectable({
  providedIn: 'root',
})
export class TooltipEnablerService {
  private tooltipList = new Array<any>();

  enableTooltip() {
    const tooltipTriggerList = [].slice.call(
      document.querySelectorAll('[data-bs-toggle="tooltip"]')
    );
    const tooltipListNewTooltips = tooltipTriggerList.map(
      (tooltipTriggerEl) => {
        return new bootstrap.Tooltip(tooltipTriggerEl);
      }
    );
    this.tooltipList.push(...tooltipListNewTooltips);
  }

  hideAllTooltips() {
    this.tooltipList;
    for (const tooltip of this.tooltipList) {
      tooltip.dispose();
    }
    this.tooltipList = new Array<any>();
  }
}
