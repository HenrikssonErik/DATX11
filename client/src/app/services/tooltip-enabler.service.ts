import { Injectable } from '@angular/core';

declare var bootstrap: any;

@Injectable({
  providedIn: 'root',
})
export class TooltipEnablerService {
  private tooltipList = new Array<any>();

  enableTooltip() {
    const tooltipTriggerList = Array.from(
      document.querySelectorAll('[data-bs-toggle="tooltip"]')
    ) as Element[];
    const tooltipListNewTooltips = tooltipTriggerList.map(
      (tooltipTriggerEl) =>
        new bootstrap.Tooltip(tooltipTriggerEl as HTMLElement)
    );
    this.tooltipList.push(...tooltipListNewTooltips);
  }

  hideAllTooltips() {
    for (const tooltip of this.tooltipList) {
      tooltip.dispose();
    }
    this.tooltipList = [];
  }
}
