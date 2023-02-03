import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Component, ElementRef, ViewChild } from '@angular/core';


@Component({
  selector: 'app-file-upload',
  templateUrl: './file-upload.component.html',
  styleUrls: ['./file-upload.component.css']
})
export class FileUploadComponent  {
  files : any [] = [];
  @ViewChild("fileUpload", { static: false })
  fileDropEl!: ElementRef;

  constructor(private http : HttpClient){}

  onFileDropped($event : any) : void{
    this.prepareFilesList($event);
  }

  fileBrowseHandler(files : any) : void {
    this.prepareFilesList(files.target.files);
  }

  deleteFile(index: number) : void {
    this.files.splice(index, 1);
  }

  prepareFilesList(files: Array<any>) : void {
    for (const item of files) {
      this.files.push(item);
    }
    this.fileDropEl.nativeElement.value = "";
  }

  formatBytes(bytes : any) : string {
    if (bytes === 0) {
      return "0 Bytes";
    }
    const k = 1024;
    const dm = 2
    const sizes = ["Bytes", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB"];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(dm)) + " " + sizes[i];
  }

  uploadFiles() {
    const formData = new FormData();
    this.files.forEach(file => formData.append('files', file, file.name));

    const httpOptions = {
      headers: new HttpHeaders({
        'Content-Type': 'multipart/form-data'
      })
    };

    console.log("Upload in progress with: ", formData );
    
    // TODO: Change to correct endpoint when it exists one.
    this.http.post('/api/upload', formData, httpOptions).subscribe({
      next: (response) => {
        //TODO: Handle the success response
      },
      error: (err) => {
        //TODO: Handle the error
      }
    });
  }
}
