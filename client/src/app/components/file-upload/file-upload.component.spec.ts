import { HttpClient, HttpClientModule } from "@angular/common/http";
import { ComponentFixture, TestBed } from "@angular/core/testing";
import { ToastrModule } from "ngx-toastr";
import { FileUploadComponent } from "./file-upload.component";
import { HttpClientTestingModule, HttpTestingController } from '@angular/common/http/testing';
import { API_URL } from 'src/environments/environment';

describe('Testing Creating the component', () => { 
  beforeEach(() => {
    TestBed.configureTestingModule({
      imports: [ HttpClientModule, ToastrModule.forRoot()],
      declarations: [FileUploadComponent],
      providers : [HttpClient]
    })
  })
  it('should create the app',(() => {
    const fixture = TestBed.createComponent(FileUploadComponent);
    const app = fixture.debugElement.componentInstance;
    expect(app).toBeTruthy();
  }));
})

describe('Testing formatBytesMethod', () => {
  let fileUploadComponent : FileUploadComponent;
  let fixture: ComponentFixture<FileUploadComponent>;
 
  beforeEach(() => {
    TestBed.configureTestingModule({
      imports: [ HttpClientModule, ToastrModule.forRoot()],
      declarations: [FileUploadComponent],
      providers : [HttpClient]
    })

    fixture = TestBed.createComponent(FileUploadComponent);
    fileUploadComponent = fixture.componentInstance;
    fixture.detectChanges();
    
  })

  it('should return "0 Bytes" for input 0', () => {
    const input = 0;
    const expected = '0 Bytes';
    const result = fileUploadComponent.formatBytes(input);
    expect(result).toEqual(expected);
  }); 

  it('should return correct result for input in kilobytes', () => {
    const input = 1048576;
    const expected = '1 MB';
    const result = fileUploadComponent.formatBytes(input);
    expect(result).toEqual(expected);
  });

  it('should return correct result for input in bytes', () => {
    const input = 1024;
    const expected = '1 KB';
    const result = fileUploadComponent.formatBytes(input);
    expect(result).toEqual(expected);
  });
})

describe('Testing deleteFile', () => {
  let fileUploadComponent : FileUploadComponent;
  let fixture: ComponentFixture<FileUploadComponent>;
  let files: File[];
 
  beforeEach(() => {
    TestBed.configureTestingModule({
      imports: [ HttpClientModule, ToastrModule.forRoot()],
      declarations: [FileUploadComponent],
      providers : [HttpClient]
    })

    fixture = TestBed.createComponent(FileUploadComponent);
    fileUploadComponent = fixture.componentInstance;
    files = [new File(['file1'], 'file1', { type: 'text/plain' }), new File(['file2'], 'file2', { type: 'text/plain' }), new File(['file3'], 'file3', { type: 'text/plain' })];
    fileUploadComponent.files = files;
    fixture.detectChanges();
    
  })

  it('should not delete a file if the index is out of bounds', () => {
    fileUploadComponent.deleteFile(-1);
    fileUploadComponent.deleteFile(3);
    expect(fileUploadComponent.files).toEqual(files);
  });

  it('should remove a file and update the index', () => {
    fileUploadComponent.deleteFile(1);
    expect(fileUploadComponent.files).toContain(files[0]);
    expect(fileUploadComponent.files).toContain(files[1]);
    expect(fileUploadComponent.files.length).toEqual(2);
  });

  
})

describe('Testing prepareFilesList', () => {
  let fileUploadComponent : FileUploadComponent;
  let fixture: ComponentFixture<FileUploadComponent>;
  let files: File[];
 
  beforeEach(() => {
    TestBed.configureTestingModule({
      imports: [ HttpClientModule, ToastrModule.forRoot()],
      declarations: [FileUploadComponent],
      providers : [HttpClient]
    })
    fixture = TestBed.createComponent(FileUploadComponent);
    fileUploadComponent = fixture.componentInstance;
    fixture.detectChanges();
    files = [new File(['file1'], 'file1', { type: 'text/plain' }), new File(['file2'], 'file2', { type: 'application/pdf' }), new File(['file3'], 'file3', { type: 'text/x-python' })];
  })

  it('should add supported files to the files list', () => {
    fileUploadComponent.prepareFilesList([files[0]]);
    fileUploadComponent.prepareFilesList([files[1]]);
    fileUploadComponent.prepareFilesList([files[2]]);
    expect(fileUploadComponent.files).toContain(files[0]);
    expect(fileUploadComponent.files).toContain(files[1]);
    expect(fileUploadComponent.files).toContain(files[2]);
  });

  it('should replace existing files with the same name in the files list', () => {
    fileUploadComponent.files = files;
    fileUploadComponent.prepareFilesList([new File(['new file1'], 'file1', { type: 'text/plain' })]);
    expect(fileUploadComponent.files[0].name).toEqual('file1');
  });

  it('should not add unsupported files to the files list', () => {
    fileUploadComponent.prepareFilesList([new File(['unsupported'], 'unsupported', { type: 'image/png' })]);
    expect(fileUploadComponent.files).toEqual([]);
  });

  it('should reset the value of fileDropEl', () => {
    fileUploadComponent.fileDropEl = { nativeElement: { value: 'file drop value' } };
    fileUploadComponent.prepareFilesList([files[0]]);
    expect(fileUploadComponent.fileDropEl.nativeElement.value).toEqual('');
  }); 
})

describe('Testing getImageType', () => {
  let fileUploadComponent : FileUploadComponent;
  let fixture: ComponentFixture<FileUploadComponent>;
 
  beforeEach(() => {
    TestBed.configureTestingModule({
      imports: [ HttpClientModule, ToastrModule.forRoot()],
      declarations: [FileUploadComponent],
      providers : [HttpClient]
    })
    fixture = TestBed.createComponent(FileUploadComponent);
    fileUploadComponent = fixture.componentInstance;
    fixture.detectChanges();
  })

  it('should return the correct image for text/plain', () => {
    const file = { name: 'test.txt', type: 'text/plain' } as File;
    const result = fileUploadComponent.getImageType(file);
    expect(result).toEqual('txt-file.png');
  });

  it('should return the correct image for text/x-python', () => {
    const file = { name: 'test.py', type: 'text/x-python' } as File;
    const result = fileUploadComponent.getImageType(file);
    expect(result).toEqual('py-file.png');
  });

  it('should return the correct image for application/pdf', () => {
    const file = { name: 'test.pdf', type: 'application/pdf' } as File;
    const result = fileUploadComponent.getImageType(file);
    expect(result).toEqual('pdf-file.png');
  });

  it('should return file.png for any other file type', () => {
    const file = { name: 'test.docx', type: 'application/vnd.openxmlformats-officedocument.wordprocessingml.document' } as File;
    const result = fileUploadComponent.getImageType(file);
    expect(result).toEqual('file.png');
  });
})

describe('Testing fileBrowseHandler', () => {
  let fileUploadComponent : FileUploadComponent;
  let fixture: ComponentFixture<FileUploadComponent>;
 
  beforeEach(() => {
    TestBed.configureTestingModule({
      imports: [ HttpClientModule, ToastrModule.forRoot()],
      declarations: [FileUploadComponent],
      providers : [HttpClient]
    })
    fixture = TestBed.createComponent(FileUploadComponent);
    fileUploadComponent = fixture.componentInstance;
    fixture.detectChanges();
  })

  it('should call prepareFilesList with the file list from the file input', () => {
   
    const mockFileList = [new File(['file1'], 'file1.txt', { type: 'text/plain' }), new File(['file2'], 'file2.txt', { type: 'text/plain' })];
    const mockFileInputEvent = { target: { files: mockFileList } } as any;
    spyOn(fileUploadComponent, 'prepareFilesList');

    fileUploadComponent.fileBrowseHandler(mockFileInputEvent);

    expect(fileUploadComponent.prepareFilesList).toHaveBeenCalledWith(mockFileList);
  });
})

describe('Testing onFileDropped', () => {
  let fileUploadComponent : FileUploadComponent;
  let fixture: ComponentFixture<FileUploadComponent>;
 
  beforeEach(() => {
    TestBed.configureTestingModule({
      imports: [ HttpClientModule, ToastrModule.forRoot()],
      declarations: [FileUploadComponent],
      providers : [HttpClient]
    })
    fixture = TestBed.createComponent(FileUploadComponent);
    fileUploadComponent = fixture.componentInstance;
    fixture.detectChanges();
  })

  it('should call prepareFilesList with the file list from the dropped event', () => {
    spyOn(fileUploadComponent, 'prepareFilesList');
    const mockFileList = [new File(['file1'], 'file1.txt', { type: 'text/plain' }), new File(['file2'], 'file2.txt', { type: 'text/plain' })];
    fileUploadComponent.onFileDropped(mockFileList);
    expect(fileUploadComponent.prepareFilesList).toHaveBeenCalledWith(mockFileList);
  });
})


describe('Testing uploadFiles', () => {
  let fileUploadComponent : FileUploadComponent;
  let fixture: ComponentFixture<FileUploadComponent>;
  let httpMock: HttpTestingController;
 
  beforeEach(() => {
    TestBed.configureTestingModule({
      imports: [ HttpClientTestingModule, ToastrModule.forRoot()],
      declarations: [FileUploadComponent],
      providers : [HttpClient]
    })
    fixture = TestBed.createComponent(FileUploadComponent);
    fileUploadComponent = fixture.componentInstance;
    httpMock = TestBed.inject(HttpTestingController);
    fixture.detectChanges();
  })

  afterEach(() => {
    httpMock.verify();
  });

  it('should upload the files to the API', () => {
    const mockFiles = [new File([], 'file1.txt'), new File([], 'file2.txt')];
    fileUploadComponent.files = mockFiles;
    fileUploadComponent.uploadFiles();
    const req = httpMock.expectOne(`${API_URL}/files`);
    expect(req.request.method).toBe('POST');
    expect(req.request.body.getAll('files').length).toBe(2);

    req.flush({});
  });  
})
