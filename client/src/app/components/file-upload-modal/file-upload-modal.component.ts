import { Component, Input } from '@angular/core';
import { NgbActiveModal } from '@ng-bootstrap/ng-bootstrap';

@Component({
  selector: 'app-file-upload-modal',
  templateUrl: './file-upload-modal.component.html',
  styleUrls: ['./file-upload-modal.component.scss'],
})
export class FileUploadModalComponent {
  //TODO: Give types to these inputs
  @Input() courseId: any;
  @Input() assignmentNumber: any;
  @Input() groupId: any;

  constructor(public activeModal: NgbActiveModal) {}
}
