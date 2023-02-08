import sys
from pathlib import Path
import unittest
import tempfile


sys.path.append(str(Path(__file__).absolute().parent.parent))

from src.test_runner import test_runner

class TestRunnerTests(unittest.TestCase):

    def setUp(self):
        self.tmp_dir = tempfile.TemporaryDirectory(suffix="__TestRunnerTests")

    def tearDown(self):
        self.tmp_dir.cleanup()

    def test_amount_of_tests_run(self):
        result = test_runner( \
            Path(__file__).parent/"test_files_test_runner"/"my_test_file.py", \
            [Path(__file__).parent/"test_files_test_runner"/f"test_{n}.py" for n in range(2)], \
            Path(self.tmp_dir.name) \
        )
        self.assertEqual(result.testsRun, 7)

    def test_wasSuccessful_false(self):
        result = test_runner( \
            Path(__file__).parent/"test_files_test_runner"/"my_test_file.py", \
            [Path(__file__).parent/"test_files_test_runner"/f"test_{n}.py" for n in range(2)], \
            Path(self.tmp_dir.name) \
        )
        self.assertFalse(result.wasSuccessful)

    def test_wasSuccessful_true(self):
        result = test_runner( \
            Path(__file__).parent/"test_files_test_runner"/"my_test_file.py", \
            [Path(__file__).parent/"test_files_test_runner"/f"test_1.py"], \
            Path(self.tmp_dir.name) \
        )
        self.assertTrue(result.wasSuccessful)

    def test_caught_fail(self):
        result = test_runner( \
            Path(__file__).parent/"test_files_test_runner"/"my_test_file.py", \
            [Path(__file__).parent/"test_files_test_runner"/f"test_{n}.py" for n in range(2)], \
            Path(self.tmp_dir.name) \
        )
        self.assertEqual(len(result.failures), 1)
        self.assertEqual(result.failures[0][0], "test_0.TestRunnerTests.test_add_fail")

    def test_caught_error(self):
        result = test_runner( \
            Path(__file__).parent/"test_files_test_runner"/"my_test_file.py", \
            [Path(__file__).parent/"test_files_test_runner"/f"test_{n}.py" for n in range(2)], \
            Path(self.tmp_dir.name) \
        )
        self.assertEqual(len(result.errors), 1)
        self.assertEqual(result.errors[0][0], "test_0.TestRunnerTests.test_add_error")

    def test_caught_skipped(self):
        result = test_runner( \
            Path(__file__).parent/"test_files_test_runner"/"my_test_file.py", \
            [Path(__file__).parent/"test_files_test_runner"/f"test_{n}.py" for n in range(2)], \
            Path(self.tmp_dir.name) \
        )
        self.assertEqual(len(result.skipped), 1)
        self.assertEqual(result.skipped[0][0], "test_0.TestRunnerTests.test_add_skip")

    def test_caught_expected_fail(self):
        result = test_runner( \
            Path(__file__).parent/"test_files_test_runner"/"my_test_file.py", \
            [Path(__file__).parent/"test_files_test_runner"/f"test_{n}.py" for n in range(2)], \
            Path(self.tmp_dir.name) \
        )
        self.assertEqual(len(result.expectedFailures), 1)
        self.assertEqual(result.expectedFailures[0][0], "test_0.TestRunnerTests.test_add_expect_fail")

    def test_caught_unexpected_success(self):
        result = test_runner( \
            Path(__file__).parent/"test_files_test_runner"/"my_test_file.py", \
            [Path(__file__).parent/"test_files_test_runner"/f"test_{n}.py" for n in range(2)], \
            Path(self.tmp_dir.name) \
        )
        self.assertEqual(len(result.unexpectedSuccesses), 1)
        self.assertEqual(result.unexpectedSuccesses[0], "test_0.TestRunnerTests.test_add_unexpected_success")
