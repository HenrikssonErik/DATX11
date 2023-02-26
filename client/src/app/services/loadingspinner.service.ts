import { Injectable } from '@angular/core';

@Injectable({
  providedIn: 'root'
})
export class LoadingspinnerService {

  public loading: boolean = false;

  constructor() { }

  setLoading(loading: boolean) {
    this.loading = loading;
  }

  getLoading(): boolean {
    return this.loading;
  }
}
