import { Injectable } from '@angular/core';

interface ResponseToToastr {
  [key: string]: string[];
}

const response_to_toastr: ResponseToToastr = {
  already_registered: [
    'You seem to be registered already. Have you forgotten your password?',
    'User with that CID is already registered!',
  ],
  cid_missing: ['CID may not be empty', 'CID is empty!'],
  email_missing: ['Email may not be empty', 'Email is empty!'],
  wrong_format: [
    'Email must be formatted as: CID@chalmers.se',
    'Wrong formatting!',
  ],
  unallowed_tokens: ['Please use letters only', 'Unallowed use of tokens!'],
  pass_not_ok: [
    'Possible characters include A-Z, a-z, 0-9, and punctuations.',
    'You cannot use those characters in the password!',
  ],
  unexpected_error: ['Something went wrong, try again!'],
  wrong_credentials: ['Did you mistype your password?', 'Could not log in'],
  cid_does_not_exist: ['CID is not correct.', 'CID is not correct.'],
  course_exists: ['This course already exists'],
  not_verified: [
    'Check your email to verify.',
    'You have not verified your account yet!',
  ],
  no_user: ['yo', 'yo'],
  already_verified: ['yo2', 'yo2'],
};

@Injectable({
  providedIn: 'root',
})
export class ToastrResponseService {
  constructor() {}

  getToastrRepsonse(status: string): string[] {
    return response_to_toastr[status];
  }
}
