import sys
from pathlib import Path
import unittest
import tempfile
import shutil
import json


sys.path.append(str(Path(__file__).absolute().parent.parent))
from src.podman.windows_test_runner import test_runner  # noqa: E402


def move_test_file(file: str | Path, dir: str | Path):
    f = Path(file)
    d = Path(dir)
    shutil.copy(f, d)


class TestRunnerTests(unittest.TestCase):

    def setUp(self):
        self.tmp_dir = tempfile.TemporaryDirectory(suffix="__TestRunnerTests")
        self.tmp_dir_path = Path(self.tmp_dir.name)/"temp"
        self.tmp_dir_path.mkdir(exist_ok=True)
        self.test_file_dir = \
            Path(__file__).parent/"test_files_test_runner"

    def tearDown(self):
        self.tmp_dir.cleanup()

    def test_amount_of_tests_run(self):
        move_test_file(self.test_file_dir/"my_test_file.py", self.tmp_dir_path)
        move_test_file(self.test_file_dir/"test_0.py", self.tmp_dir_path)
        move_test_file(self.test_file_dir/"test_1.py", self.tmp_dir_path)

        result = json.loads(test_runner(self.tmp_dir_path))

        self.assertEqual(result["tests_run"], 10)

    def test_was_successful_false(self):
        move_test_file(self.test_file_dir/"my_test_file.py", self.tmp_dir_path)
        move_test_file(self.test_file_dir/"test_0.py", self.tmp_dir_path)
        move_test_file(self.test_file_dir/"test_1.py", self.tmp_dir_path)
        result = json.loads(test_runner(self.tmp_dir_path))

        self.assertFalse(result["was_successful"])

    def test_was_successful_true(self):
        move_test_file(self.test_file_dir/"my_test_file.py", self.tmp_dir_path)
        move_test_file(self.test_file_dir/"test_1.py", self.tmp_dir_path)

        result = json.loads(test_runner(self.tmp_dir_path))

        self.assertTrue(result["was_successful"])

    def test_caught_fail(self):
        move_test_file(self.test_file_dir/"my_test_file.py", self.tmp_dir_path)
        move_test_file(self.test_file_dir/"test_0.py", self.tmp_dir_path)
        move_test_file(self.test_file_dir/"test_1.py", self.tmp_dir_path)

        result = json.loads(test_runner(self.tmp_dir_path))

        self.assertEqual(len(result["failures"]), 1)
        self.assertEqual(result["failures"][0][0],
                         "test_0.TestRunnerTests.test_add_fail")

    def test_caught_error(self):
        move_test_file(self.test_file_dir/"my_test_file.py", self.tmp_dir_path)
        move_test_file(self.test_file_dir/"test_0.py", self.tmp_dir_path)
        move_test_file(self.test_file_dir/"test_1.py", self.tmp_dir_path)

        result = json.loads(test_runner(self.tmp_dir_path))

        self.assertEqual(len(result["errors"]), 1)
        self.assertEqual(result["errors"][0][0],
                         "test_0.TestRunnerTests.test_add_error")

    def test_caught_skipped(self):
        move_test_file(self.test_file_dir/"my_test_file.py", self.tmp_dir_path)
        move_test_file(self.test_file_dir/"test_0.py", self.tmp_dir_path)
        move_test_file(self.test_file_dir/"test_1.py", self.tmp_dir_path)

        result = json.loads(test_runner(self.tmp_dir_path))

        self.assertEqual(len(result["skipped"]), 1)
        self.assertEqual(result["skipped"][0][0],
                         "test_0.TestRunnerTests.test_add_skip")

    def test_caught_expected_fail(self):
        move_test_file(self.test_file_dir/"my_test_file.py", self.tmp_dir_path)
        move_test_file(self.test_file_dir/"test_0.py", self.tmp_dir_path)
        move_test_file(self.test_file_dir/"test_1.py", self.tmp_dir_path)

        result = json.loads(test_runner(self.tmp_dir_path))

        self.assertEqual(len(result["expected_failures"]), 1)
        self.assertEqual(
            result["expected_failures"][0][0],
            "test_0.TestRunnerTests.test_add_expect_fail"
        )

    def test_caught_unexpected_success(self):
        move_test_file(self.test_file_dir/"my_test_file.py", self.tmp_dir_path)
        move_test_file(self.test_file_dir/"test_0.py", self.tmp_dir_path)
        move_test_file(self.test_file_dir/"test_1.py", self.tmp_dir_path)

        result = json.loads(test_runner(self.tmp_dir_path))

        self.assertEqual(len(result["unexpected_successes"]), 1)
        self.assertEqual(
            result["unexpected_successes"][0],
            "test_0.TestRunnerTests.test_add_unexpected_success"
        )
