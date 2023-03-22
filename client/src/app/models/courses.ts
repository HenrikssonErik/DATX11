export interface Courses {
  Courses: Course[];
}

export interface Course {
  Assignments: any[]; // change "any" when we know how it will look
  Course: string;
  Role: string;
  StudyPeriod: number;
  Year: number;
  courseID: number;
}
