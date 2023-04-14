# test python file

import unittest

import my_test_file


class TestRunnerTests(unittest.TestCase):
    def test_mul(self):
        self.assertEqual(my_test_file.mul(3, 5), 3 * 5)

    def test_add(self):
        self.assertEqual(my_test_file.add(10, 35), 10 + 35)

    def test_add_mul(self):
        self.assertEqual(
            my_test_file.add(
                my_test_file.mul(3, 5),
                my_test_file.mul(5, 3)
            ),
            3*5 + 5*3
        )

    def test_mul_add(self):
        self.assertEqual(
            my_test_file.mul(
                my_test_file.add(3, 5),
                my_test_file.add(5, 3)
            ),
            (3+5) * (5+3)
        )
