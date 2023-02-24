import { Injectable } from '@angular/core';

@Injectable({
  providedIn: 'root'
})
export class UploadUnitTestConfigService {

  endpoint : string; 
  allowedFileTypes: string[];
  allowedFileTypesForPrint : string [];
  showFeedback : boolean;

  constructor() {
    this.endpoint = 'unitTest'
    this.allowedFileTypes = ['text/x-python'];
    this.allowedFileTypesForPrint = ['.py'];
    this.showFeedback = false;
   }
}
