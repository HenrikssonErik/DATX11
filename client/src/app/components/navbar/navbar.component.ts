import { Component, Renderer2, OnInit, AfterViewInit } from '@angular/core';
import * as $ from 'jquery';

@Component({
  selector: 'app-navbar',
  templateUrl: './navbar.component.html',
  styleUrls: ['./navbar.component.scss']
})
export class NavbarComponent implements OnInit, AfterViewInit {

  constructor(private renderer: Renderer2) { }

  ngOnInit(): void {

    this.renderer.listen('window', 'scroll', (event) => {
      if (window.scrollY > 50) {
        this.renderer.addClass(document.querySelector('.nav'), 'affix');
      } else {
        this.renderer.removeClass(document.querySelector('.nav'), 'affix');
      }
    });
  }

  ngAfterViewInit(): void {
  
    $('.navTrigger').click(function() {
      $(this).toggleClass('active');
      $("#mainListDiv").toggleClass("show_list");
      $("#mainListDiv").fadeIn();
    });
  }
  

}
