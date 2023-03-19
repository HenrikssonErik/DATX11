import { Component, OnInit } from '@angular/core';

@Component({
  selector: 'app-home-page',
  templateUrl: './home-page.component.html',
  styleUrls: ['./home-page.component.scss'],
})
export class HomePageComponent implements OnInit {
  quotes: Map<string, string> = new Map<string, string>();

  constructor() {}

  ngOnInit(): void {
    this.quotes.set(
      'Martin Golding',
      'Always code as if the guy who ends up maintaining your code will be a violent psychopath who knows where you live.'
    );
    this.quotes.set(
      'Steve Maguire',
      'Never allow the same bug to bite you twice.'
    );
    this.quotes.set(
      'Seymour Cray',
      'The trouble with programmers is that you can never tell what a programmer is doing until it’s too late.'
    );
    this.quotes.set(
      'Gerald Weinberg',
      'If builders built buildings the way programmers wrote programs, then the first woodpecker that came along would destroy civilization.'
    );
    this.quotes.set(
      'T. DeMarco and T. Lister',
      'Quality is free, but only to those who are willing to pay heavily for it'
    );
    this.quotes.set(
      'Anonymous',
      'The bitterness of poor quality remains long after the sweetness of meeting the schedule has been forgotten.'
    );
    this.quotes.set(
      'Boris Beizer',
      'Software never was perfect and won’t get perfect. But is that a license to create garbage? The missing ingredient is our reluctance to quantify quality'
    );
    this.quotes.set(
      'Anonymous',
      'Software testing proves the existence of bugs not their absence.'
    );
    this.quotes.set(
      'Anonymous',
      'If you don’t like unit testing your product, most likely your customers won’t like to test it either.'
    );
    this.quotes.set(
      'Anonymous',
      'Just because you’ve counted all the trees doesn’t mean you’ve seen the forest.'
    );
    this.quotes.set(
      'Anonymous',
      'Software testers always go to heaven; they’ve already had their fair share of hell.'
    );
    this.quotes.set(
      'Anonymous',
      'The principle objective of software testing is to give confidence in the software.'
    );
    this.quotes.set(
      'Anonymous',
      'f u cn rd ths, u cn gt a gd jb n sftwr tstng.'
    );
    this.quotes.set('Anonymous', 'All code is guilty, until proven innocent.');
    this.quotes.set(
      'Anonymous',
      'Why do we never have time to do it right, but always have time to do it over?'
    );

    console.log(this.quotes);
  }
}
