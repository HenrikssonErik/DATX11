import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Component, ElementRef, ViewChild } from '@angular/core';
import { ToastrService } from 'ngx-toastr';
import { API_URL } from 'src/environments/environment';

@Component({
  selector: 'app-file-upload',
  templateUrl: './file-upload.component.html',
  styleUrls: ['./file-upload.component.css'],
})
export class FileUploadComponent {
  files: File[] = [];
  @ViewChild('fileUpload', { static: false })
  fileDropEl!: ElementRef;

  constructor(private http: HttpClient, private toastr: ToastrService) {}

  /**
  * Method to handle the file drop event and prepares the list of files
  * @param {any} $event - Event object that holds the dropped files
  * @return {void}
  */
  onFileDropped($event : any): void {
    this.prepareFilesList($event);
  }

/**
 * fileBrowseHandler
 * Handles the file selection event from the file input element.
 * @param files {Event} The change event emitted by the file input element
 * @returns void
 */
  fileBrowseHandler(files : Event): void {
    let fileInput: HTMLInputElement = files.target as HTMLInputElement;
    let fileList: FileList | null = fileInput.files;
    if (fileList) {
      this.prepareFilesList(Array.from(fileList));
    }
  }

  /**
 * Called in click method when user wants to remove an uploaded file.
 * Deletes a file from the `files` array.
 * @param {number} index - The index of the file to delete.
 * @returns {void}
 */
  deleteFile(index: number): void {
    this.files.splice(index, 1);
  }

  prepareFilesList(files: Array<File>): void {
    const allowedTypes = ['application/python', 'application/pdf', 'text/plain'];
    for (const file of files) {
      const index = this.files.findIndex(f => f.name === file.name);
      if (allowedTypes.includes(file.type)) {
        if (index !== -1) {
          this.files[index] = file;
          this.toastr.info('File was replaced with duplicate', 'Duplicate file', {
            closeButton: true,
          });
        } else {
          this.files.push(file);
        }
      }else {
        this.toastr.warning('That file type is not supported', 'Wrong file type', {
          closeButton: true,
        });
      }
    }
    this.fileDropEl.nativeElement.value = '';
  }

  /**
  * This method formats the file size in bytes to a human-readable format, with units such as KB,
  * MB,  etc.
  * @param {number} bytes - a number representing the size of a file in bytes.
  * @returns {string} a string representation of the file size with the unit of measurement.
  */
  formatBytes(bytes: number): string {
    if (bytes === 0) {
      return '0 Bytes';
    }
    const k = 1024;
    const dm = 2;
    const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB', 'PB', 'EB', 'ZB', 'YB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(dm)) + ' ' + sizes[i];
  }

  /**
 * uploadFiles - method to upload files to the server
 *
 * @returns {void}
 */
  uploadFiles() : void {
    const formData = new FormData();
    this.files.forEach((file : File) : void => formData.append('files', file, file.name));
  
    this.http.post(`${API_URL}/files`, formData).subscribe({
      next: (response ) => {
        //TODO: Handle the success response
      },
      error: (err) => {
        //TODO: Handle the error
      },
    });
  }
}
