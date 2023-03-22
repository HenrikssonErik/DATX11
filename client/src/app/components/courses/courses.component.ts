import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Component, OnInit } from '@angular/core';
import { User } from 'src/app/models/user';
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
    this.userService.getUserData().subscribe((res: User) => {
      console.log(res);
    });
  }
}
