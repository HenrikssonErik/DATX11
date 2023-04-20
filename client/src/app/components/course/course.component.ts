import { Component, Input, OnInit } from '@angular/core';
import { Router } from '@angular/router';
import { Course } from 'src/app/models/courses';

@Component({
  selector: 'app-course',
  templateUrl: './course.component.html',
  styleUrls: ['./course.component.scss'],
})
export class CourseComponent implements OnInit {
  @Input() data: Course | undefined;

  constructor(private router: Router) {}

  cardColors = [
    { name: 'Green', value: '#e1ece4' },
    { name: 'Purple', value: '#d3d2ff' },
    { name: 'Yellow', value: '#fbeeb2' },
    { name: 'Red', value: '#f6c4d2' },
    { name: 'Blue', value: '#b7e1f5' },
  ];

  primaryColor: string = '#e1ece4';
  secondaryColor: string = '#c5d2c1';

  ngOnInit(): void {
    console.log(this.data);
  }

  goToCourse(id: number) {
    this.router.navigate([`courses/${id}`]);
  }

  changeCardColor(color: any) {
    //TODO: Create a cardColorService where the users picks are stored and retrieved in DB. Also maybe create an option to pick a custom one.
    this.primaryColor = color.value;
    if (color.value == '#e1ece4') {
      this.secondaryColor = '#c5d2c1';
    } else if (color.value == '#d3d2ff') {
      this.secondaryColor = '#a1a0c5';
    } else if (color.value == '#fbeeb2') {
      this.secondaryColor = '#d1cfa7';
    } else if (color.value == '#f6c4d2') {
      this.secondaryColor = '#d8b7c1';
    } else if (color.value == '#b7e1f5') {
      this.secondaryColor = '#92b8cf';
    } else {
      this.secondaryColor = '#fff';
    }
  }
}
