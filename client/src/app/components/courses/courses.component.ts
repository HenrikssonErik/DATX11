import { HttpClient, HttpHeaders, HttpResponse } from '@angular/common/http';
import { Component, OnInit } from '@angular/core';
import { API_URL } from 'src/environments/environment';

@Component({
  selector: 'app-courses',
  templateUrl: './courses.component.html',
  styleUrls: ['./courses.component.scss'],
})
export class CoursesComponent implements OnInit {
  constructor(private http: HttpClient) {}

  ngOnInit(): void {
    const cookie = this.replaceSessionToken(document.cookie);
    console.log(cookie);

    const data = {
      Group: 3,
      User: 32,
      Course: 6,
    };

    let headers = new HttpHeaders();
    headers = headers.append('Cookies', cookie);
    this.http
      .post(`${API_URL}/removeFromGroup`, data, { headers })
      .subscribe((res) => {
        console.log(res);
      });
  }

  replaceSessionToken(inputString: string): string {
    const splitString = inputString.split('=');
    const newString = `Token=${splitString[1]}`;
    return newString;
  }
}
