# test python file

import unittest
import my_test_file


class TestRunnerTests(unittest.TestCase):
    def test_add(self):
        self.assertEqual(my_test_file.add(1, 1), 1 + 1)

    def test_add_fail(self):
        self.assertEqual(my_test_file.add(1, 1), 0)

    def test_add_error(self):
        a  # noqa: F821

    @unittest.skip("test")
    def test_add_skip(self):
        pass

    @unittest.expectedFailure
    def test_add_expect_fail(self):
        self.assertEqual(my_test_file.add(1, 1), 0)

    @unittest.expectedFailure
    def test_add_unexpected_success(self):
        self.assertEqual(my_test_file.add(1, 1), 1+1)
