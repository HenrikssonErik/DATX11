export interface User {
  id?: number;
  cid: string;
  email: string;
  fullname: string;
  role?: string;
}

export interface Users {
  Users: User[];
}
