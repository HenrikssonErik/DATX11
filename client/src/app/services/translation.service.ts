import { Injectable } from '@angular/core';
import { TranslateService } from '@ngx-translate/core';

@Injectable({
  providedIn: 'root',
})
export class TranslationService {
  constructor(private translate: TranslateService) {}

  setLanguage(language: string): void {
    this.translate.setDefaultLang(language);
    localStorage.setItem('language', language);
  }

  getLanguage(): string {
    const language = localStorage.getItem('language') || 'en';
    this.translate.setDefaultLang(language);
    return language;
  }

  switchLanguage(language: string): void {
    this.translate.use(language);
    localStorage.setItem('language', language);
  }
}
