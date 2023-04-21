import unittest
from timeout_decorator import timeout


# Every method that start with `test_` in this class will be run as a test.
class TestTemplate(unittest.TestCase):

    def setUp(self):
        # Setup for tests, this will run before every test.
        # https://docs.python.org/3/library/unittest.html#unittest.TestCase.setUp
        pass

    def tearDown(self):
        # Teardown for test, this will run after every test.
        # https://docs.python.org/3/library/unittest.html#unittest.TestCase.tearDown
        pass

    @timeout(10)  # Fails after `10` sec
    def test_(self):
        # Available asserts: https://docs.python.org/3/library/unittest.html#unittest.TestCase.assertEqual
        # TODO: Write your own test.
        pass
