import { Injectable } from '@angular/core';

@Injectable({
  providedIn: 'root'
})
export class UploadUnitTestConfigService {

  endpoint : string; 
  allowedFileTypes: string[];

  constructor() {
    this.endpoint = 'unitTest'
    this.allowedFileTypes = ['text/x-python'];
   }
}
