import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Component, OnInit } from '@angular/core';
import { UserService } from 'src/app/services/user-service.service';
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

  constructor(private http: HttpClient, private userService: UserService) {}

  ngOnInit(): void {
    //this.getCourses();

    this.userService.getUserData();
  }

  getCourses() {
    let headers = new HttpHeaders();
    headers = headers.append('Cookies', document.cookie);
    this.http.get(`${API_URL}/getCourses`, { headers }).subscribe((res) => {
      this.courses = res;
    });
  }
}
