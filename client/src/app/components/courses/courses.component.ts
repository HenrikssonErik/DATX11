import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Component, OnInit } from '@angular/core';
import { API_URL } from 'src/environments/environment';

@Component({
  selector: 'app-courses',
  templateUrl: './courses.component.html',
  styleUrls: ['./courses.component.scss'],
})
export class CoursesComponent implements OnInit {
  courses: any;
  events = [];
  deadlines = [];

  constructor(private http: HttpClient) {}

  ngOnInit(): void {
    this.getCourses();
  }

  getCourses() {
    const cookie = this.replaceSessionToken(document.cookie);

    let headers = new HttpHeaders();
    headers = headers.append('Cookies', cookie);
    this.http.get(`${API_URL}/getCourses`, { headers }).subscribe((res) => {
      this.courses = res;
      console.log(this.courses);
    });
  }

  replaceSessionToken(inputString: string): string {
    const splitString = inputString.split('=');
    const newString = `Token=${splitString[1]}`;
    return newString;
  }
}
