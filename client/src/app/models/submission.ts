export interface TestResult {
  Grade: null | boolean;
  Submission: number;
  teacherfeedback: null | string;
  testfeedback: {
    general_tests_feedback: {
      PEP8_results: string;
      tested_file: {
        file: string;
        file_name: string;
        file_type: string;
      };
    }[];
    unittest_feedback: {
      errors: [string, string][];
      expected_failures: string[];
      successes: string[];
      failures: string[];
      skipped: string[];
      tests_run: number;
      unexpected_successes: string[];
      was_successful: boolean;
    };
  };
  testpass: boolean;
  GradedBy: string;
}

export interface AssignmentSubmission {
  dateSubmitted: string;
  lastEdited: string;
  Feedback: string | null;
  GradedBy: string;
  Score: number;
  grade: boolean | null;
  groupid: number;
  testpass: boolean;
  Submission: number;
  GroupNumber: number;
}

export interface Submission {
  Assignment: number;
  Submissions: AssignmentSubmission[];
}
