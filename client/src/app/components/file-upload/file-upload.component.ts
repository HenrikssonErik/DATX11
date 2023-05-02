import { HttpClient, HttpHeaders, HttpResponse } from '@angular/common/http';
import { Component, ElementRef, Input, ViewChild } from '@angular/core';
import { ToastrService } from 'ngx-toastr';
import { API_URL } from 'src/environments/environment';
import { EventEmitter } from '@angular/core';
import { NgbActiveModal } from '@ng-bootstrap/ng-bootstrap';

@Component({
  selector: 'app-file-upload',
  templateUrl: './file-upload.component.html',
  styleUrls: ['./file-upload.component.scss'],
})
export class FileUploadComponent {
  files: File[] = [];
  @ViewChild('fileUpload', { static: false })
  fileDropEl!: ElementRef;

  @Input() courseId!: number;
  @Input() assignmentNumber!: number;
  @Input() groupId!: number;
  isLoading: boolean = false;

  allowedFileTypes: string[] = [
    'text/x-python',
    'application/pdf',
    'text/plain',
  ];
  allowedFileTypesForPrint: string[] = ['.py', '.pdf', '.txt'];

  generalTestFeedback: any[] = [];

  constructor(
    private http: HttpClient,
    private toastr: ToastrService,
    private modalService: NgbActiveModal
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
   * Called in click method when user wants to remove an uploaded file.
   * Deletes a file from the `files` array.
   * @param {number} index - The index of the file to delete.
   * @returns {void}
   */
  deleteFile(index: number): void {
    this.files.splice(index, 1);
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
    this.isLoading = true;
    const headers: HttpHeaders = new HttpHeaders().append(
      'Cookies',
      document.cookie
    );

    const formData = new FormData();
    this.files.forEach((file: File): void =>
      formData.append('files', file, file.name)
    );

    formData.append('Course', this.courseId.toString());
    formData.append('Assignment', this.assignmentNumber.toString());
    formData.append('Group', this.groupId.toString());

    this.http
      .post<HttpResponse<any>>(`${API_URL}/files`, formData, {
        observe: 'response',
        headers: headers,
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
              'The assignment was succesfully submitted',
              'Sucess!',
              {
                closeButton: true,
              }
            );

            //TODO: Handle this in complete() instead?
          }

          // TODO: This can be removed unless we want to use it directly.
          for (const file of response.body.general_tests_feedback) {
            const generalTestItem = {
              file: file.tested_file,
              pep8_results: file.PEP8_results,
            };

            this.generalTestFeedback.push(generalTestItem);
          }

          console.log(response);

          //TODO: Handle the success response
        },
        error: (err) => {
          this.isLoading = false;
          this.modalService.close();
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
        complete: () => {
          this.isLoading = false;
          this.modalService.close();
          //TODO: Handle the updated feedback without reloading the page
          location.reload();
        },
      });
  }

  //this method if called will get a file from the serverand download it
  getFiles(): void {
    this.http
      .get(`${API_URL}/getAssignmentFiles`, {
        observe: 'response',
        responseType: 'blob',
      })
      .subscribe({
        next: (response) => {
          const contentDispositionHeader = response.headers.getAll(
            'Content-Disposition'
          )![0];
          const filename = contentDispositionHeader
            .split(';')[1]
            .split('=')[1]
            .replace(/"/g, '')
            .trim();
          console.log(filename);
          console.log(response.body);
          var file = new File([response.body!], 'assignment');

          const url = URL.createObjectURL(file);
          const link = document.createElement('a');
          link.href = url;
          link.download = filename;
          link.click();
        },
        error: (err) => {
          //TODO: Handle the error
        },
      });
  }
}
