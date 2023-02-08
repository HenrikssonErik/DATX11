# test python file

import unittest

import my_test_file
class TestRunnerTests(unittest.TestCase):
    def test_mul(self):
        self.assertEqual(my_test_file.mul(3, 5), 3 * 5)