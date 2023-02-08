from pathlib import Path
import shutil
import unittest




def test_runner(file: Path, tests: list[Path], run_directory: Path) -> unittest.TestResult:
    """
    This function copy's the `file` and `tests` to the `run_directory` and then puts all 
    the `tests` in to a test suite. Then the tests are run and the result is returned back 
    to the calle.

    Takes in:
        file: `pathlib.Path` to the file which should be tested.
        tests: `list[pathlib.Path]` to the test files which should be run on the file.
        run_directory: `pathlib.Path` to the directory where the file will be tested with 
        the given tests.

    Returns: a `unittest.TestResult` which is where the results of the tests is stored.

    Note:
    Currently it is up to the calle to ensure that the run_directory does not have any files 
    of the same names as the the `file` or `tests`.
    """

    # receive tests from DB (currently we take them in as parameters)
    # execute the tests on the python file
    # return the result

    # look at: 
    # https://stackoverflow.com/questions/284043/outputting-data-from-unit-test-in-python
    # https://stackoverflow.com/a/284192/11933712
    # https://docs.python.org/3/library/unittest.html#unittest.TestCase


    shutil.copy(str(file.absolute()), run_directory)

    for test in tests:
        shutil.copy(str(test.absolute()), run_directory)

    test_suit = unittest.TestLoader().discover(str(run_directory), pattern="test_*.py")

    results = test_suit.run(unittest.TestResult(verbosity=2))

    return results

