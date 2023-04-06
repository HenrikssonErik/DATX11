import { HttpClient, HttpHeaders, HttpResponse } from '@angular/common/http';
import { Component, ElementRef, ViewChild } from '@angular/core';
import { NgbActiveModal } from '@ng-bootstrap/ng-bootstrap';
import { ToastrService } from 'ngx-toastr';
import { API_URL } from 'src/environments/environment';

@Component({
  selector: 'app-file-upload-modal',
  templateUrl: './file-upload-modal.component.html',
  styleUrls: ['./file-upload-modal.component.scss'],
})
export class FileUploadModalComponent {
  files: File[] = [];
  @ViewChild('fileUpload', { static: false })
  fileDropEl!: ElementRef;
  endpoint = 'files';
  allowedFileTypes = ['text/x-python', 'application/pdf', 'text/plain'];
  allowedFileTypesForPrint = ['.py', '.pdf', '.txt'];

  testFeedBackArray: any[] = [];
  constructor(
    public activeModal: NgbActiveModal,
    private http: HttpClient,
    private toastr: ToastrService
  ) {}

  /**
   * Method to handle the file drop event and prepares the list of files
   * @param {any} $event - Event object that holds the dropped files
   * @return {void}
   */
  onFileDropped($event: any): void {
    this.prepareFilesList($event);
  }

  /**
   * fileBrowseHandler
   * Handles the file selection event from the file input element.
   * @param files {Event} The change event emitted by the file input element
   * @returns void
   */
  fileBrowseHandler(files: Event): void {
    let fileInput: HTMLInputElement = files.target as HTMLInputElement;
    let fileList: FileList | null = fileInput.files;
    if (fileList) {
      this.prepareFilesList(Array.from(fileList));
    }
  }

  /**
   * Adds/updates allowed file types to files list
   * @param {Array<File>} files - Array of selected files
   * @returns {void}
   */
  prepareFilesList(files: Array<File>): void {
    const allowedTypes = this.allowedFileTypes;
    for (const file of files) {
      const index = this.files.findIndex((f) => f.name === file.name);
      if (allowedTypes.includes(file.type)) {
        if (index !== -1) {
          this.files[index] = file;
          this.toastr.info(file.name + ' was replaced', 'Duplicate file', {
            closeButton: true,
          });
        } else {
          this.files.push(file);
        }
      } else {
        this.toastr.warning(
          file.type + ' is not supported',
          'Unsupported file type',
          {
            closeButton: true,
          }
        );
      }
    }
    this.fileDropEl.nativeElement.value = '';
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

  getImageType(file: File): string {
    if (file.type === 'text/plain') {
      return 'txt-file.png';
    }
    if (file.type === 'text/x-python') {
      return 'py-file.png';
    }
    if (file.type === 'application/pdf') {
      return 'pdf-file.png';
    }
    return 'file.png';
  }

  /**
   * uploadFiles - method to upload files to the server
   *
   * @returns {void}
   */
  uploadFiles(): void {
    let header: HttpHeaders = new HttpHeaders();
    header = header.append('Content-Type', 'application/json');

    const formData = new FormData();
    this.files.forEach((file: File): void =>
      formData.append('files', file, file.name)
    );

    this.http
      .post<HttpResponse<any>>(`${API_URL}/` + this.endpoint, formData, {
        observe: 'response',
      })
      .subscribe({
        // TODO: Initiate loading
        // TODO: Check if we shouldnt remove next: why even have it?
        next: (response: any) => {
          /** Code below is to typecast the any-response to the tuple we get back from file_handler.
           * Since this tuple may yet be subject to change, we will not typecast it right now. To be set.
           */
          //const tupleResponse = response as {feedback: Array<[string, string]>, number_of_files: string}
          //console.log(tupleResponse.number_of_files);

          if (response.status == 200) {
            this.toastr.success(
              'The file was successfully uploaded',
              'Sucess!',
              {
                closeButton: true,
              }
            );

            //TODO: Stop loading.
          }

          console.log(response);

          for (const file of response.body.feedback) {
            const testFeedBackItem = {
              file: file.tested_file,
              fileContent: file.PEP8_results,
            };

            this.testFeedBackArray.push(testFeedBackItem);
          }

          //TODO: Handle the success response
        },
        error: (err) => {
          this.toastr.error(
            err.error.number_of_files,
            'Something went wrong!',
            {
              closeButton: true,
            }
          );
          console.log(err.error);
          //TODO: Handle the error
        },
      });
  }
}
