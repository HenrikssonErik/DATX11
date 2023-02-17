import { Injectable } from '@angular/core';

@Injectable({
  providedIn: 'root'
})
export class UploadFileConfigService {

  endpoint : string; 
  allowedFileTypes: string[];

  constructor() {
    this.endpoint = 'files'
    this.allowedFileTypes = ['text/x-python', 'application/pdf', 'text/plain'];
   }
}
