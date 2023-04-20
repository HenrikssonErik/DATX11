import { Component, Input } from '@angular/core';
import { NgbActiveModal } from '@ng-bootstrap/ng-bootstrap';

@Component({
  selector: 'app-file-upload-modal',
  templateUrl: './file-upload-modal.component.html',
  styleUrls: ['./file-upload-modal.component.scss'],
})
export class FileUploadModalComponent {
  @Input() courseId!: number;
  @Input() assignmentNumber!: number;
  @Input() groupId!: number;

  constructor(public activeModal: NgbActiveModal) {}
}
