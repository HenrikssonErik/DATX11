import { Injectable } from '@angular/core';

@Injectable({
  providedIn: 'root'
})
export class UploadFileConfigService {

  endpoint : string; 
  allowedFileTypes: string[];
  allowedFileTypesForPrint : string [];
  showFeedback : boolean;

  constructor() {
    this.endpoint = 'files'
    this.allowedFileTypes = ['text/x-python', 'application/pdf', 'text/plain'];
    this.allowedFileTypesForPrint = ['.py', '.pdf' , '.txt'];
    this.showFeedback = true;
   }
}
