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
      expected_failures: never[];
      successes: never[];
      failures: never[];
      skipped: never[];
      tests_run: number;
      unexpected_successes: never[];
      was_successful: boolean;
    };
  };
  testpass: boolean;
  GradedBy: string;
}

export interface AssignmentSubmission {
  Date: string;
  Feedback: string | null;
  GradedBy: string;
  Score: number;
  grade: boolean | null;
  groupid: number;
  testpass: boolean;
  Submission: number;
}

export interface Submission {
  Assignment: number;
  Submissions: AssignmentSubmission[];
}
