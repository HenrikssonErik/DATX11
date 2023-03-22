import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { API_URL } from 'src/environments/environment';

@Injectable({
  providedIn: 'root',
})
export class UserService {
  constructor(private http: HttpClient) {}

  getUserData() {
    let headers = new HttpHeaders();
    headers = headers.append('Cookies', document.cookie);
    this.http.get(`${API_URL}/getUserInfo`, { headers }).subscribe((res) => {
      console.log(res);
    });
  }
}
