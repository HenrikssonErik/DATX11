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
    const nav : Element | null = document.querySelector('.nav');
    if(!nav){
      return;
    }

    const classList : DOMTokenList = nav.classList;

    this.renderer.listen('window', 'scroll', (event) => {
      if (window.scrollY > 50) {
        classList.add('affix');
      } else {
        classList.remove('affix');
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
