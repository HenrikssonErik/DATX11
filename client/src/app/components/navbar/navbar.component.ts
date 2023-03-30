import {
  Component,
  Renderer2,
  OnInit,
  AfterViewInit,
  SimpleChanges,
  OnChanges,
} from '@angular/core';
import * as $ from 'jquery';
import { AuthService } from 'src/app/services/auth.service';

@Component({
  selector: 'app-navbar',
  templateUrl: './navbar.component.html',
  styleUrls: ['./navbar.component.scss'],
})
export class NavbarComponent implements OnInit, AfterViewInit {
  isLoggedIn: boolean = false;

  constructor(private renderer: Renderer2, private authService: AuthService) {}

  ngOnInit(): void {
    /* this.authService.isAuthenticated.subscribe(
      (isAuthenticated) => (this.isLoggedIn = isAuthenticated)
    ); */

    this.authService.isAuthenticated.subscribe((element) => {
      this.isLoggedIn = element;
      console.log(element);
    });

    const nav: Element | null = document.querySelector('.nav');
    if (!nav) {
      return;
    }

    const classList: DOMTokenList = nav.classList;

    this.renderer.listen('window', 'scroll', (event) => {
      if (window.scrollY > 50) {
        classList.add('affix');
      } else {
        classList.remove('affix');
      }
    });
  }

  ngAfterViewInit(): void {
    $('.navTrigger').click(function () {
      $(this).toggleClass('active');
      $('#mainListDiv').toggleClass('show_list');
      $('#mainListDiv').fadeIn();
    });
  }

  logOut() {
    this.authService.logOut();
  }
}
