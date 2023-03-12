import { ChangeDetectorRef, Component, OnDestroy, OnInit } from '@angular/core';
import { TranslationService } from 'src/app/services/translation.service';

@Component({
  selector: 'app-footer',
  templateUrl: './footer.component.html',
  styleUrls: ['./footer.component.scss'],
})
export class FooterComponent implements OnInit {
  selectedLanguage: string = '';
  imagePath: string = '';
  constructor(
    private translateService: TranslationService,
    private cdr: ChangeDetectorRef
  ) {}

  ngOnInit(): void {
    const lang: string = this.translateService.getLanguage();
    if (lang == 'se') {
      this.selectedLanguage = 'Swedish';
      this.imagePath = 'se.png';
    } else {
      this.selectedLanguage = 'English';
      this.imagePath = 'en.png';
    }
  }

  changeLanguage(lang: string) {
    if (lang == 'se') {
      this.selectedLanguage = 'Swedish';
      this.imagePath = 'se.png';
    } else {
      this.selectedLanguage = 'English';
      this.imagePath = 'en.png';
    }
    this.translateService.switchLanguage(lang);
    this.cdr.detectChanges();

    console.log(this.selectedLanguage);
  }
}
