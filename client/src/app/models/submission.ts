export interface Submission {
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
      failures: never[];
      skipped: never[];
      tests_run: number;
      unexpected_successes: never[];
      was_successful: boolean;
    };
  };
  testpass: boolean;
}
