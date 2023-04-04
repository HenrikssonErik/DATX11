export interface Courses {
  courses: Course[];
}

export interface Course {
  Assignments: Assignment[]; // change "any" when we know how it will look
  Course: string;
  CourseName: string;
  Role: string;
  StudyPeriod: number;
  Year: number;
  courseID: number;
}

export interface Assignment {
  AssignmentNr: number;
  Description: string;
  DueDate: Date;
}
