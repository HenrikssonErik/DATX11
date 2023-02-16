from pathlib import Path
import sys
import subprocess
import json
from dataclasses import dataclass
import inspect
import textwrap
import functools


@functools.cache
def _generate_executer() -> str:
    """This function generates the python code for the executor

    This is a kinda hacky way of getting all the benefits of our ide and
    returning the content of `__code` as a str.
    """
    def __code():
        import unittest
        import json
        import sys

        # This script should be started in a new instance of python and then
        # will print the tests results to stdout in a json format
        if __name__ == "__main__":
            test_dir = sys.argv[1]
            test_suit = unittest.TestLoader().discover(
                test_dir, pattern="test_*.py"
            )
            results = test_suit.run(unittest.TestResult(verbosity=2))
            json_result = {
                "tests_run": results.testsRun,
                "was_successful": results.wasSuccessful(),
                "errors": [(e[0].id(), e[1]) for e in results.errors],
                "failures": [(e[0].id(), e[1]) for e in results.failures],
                "expected_failures": [
                    (e[0].id(), e[1]) for e in results.expectedFailures
                ],
                "unexpected_successes": [
                    e.id() for e in results.unexpectedSuccesses
                ],
                "skipped": [(e[0].id(), e[1]) for e in results.skipped],
            }

            print(json.dumps(json_result))

    return textwrap.dedent(
        inspect.getsource(__code).replace("def __code():", "")
    )


@dataclass
class TestResults:
    """
    A dataclass to store the results of the tests that have been run.
    """
    tests_run: int
    was_successful: bool
    errors: list[tuple[str, str]]
    failures: list[tuple[str, str]]
    expected_failures: list[tuple[str, str]]
    unexpected_successes: list[str]
    skipped: list[tuple[str, str]]


def test_runner(run_directory: Path) -> TestResults:
    """Runs all the tests in the specified directory

    Parameters
    ----------
    `run_directory` : Path
        A path to the directory where the test files and the python file we
        are going to test

    Returns
    -------
    TestResults
        the results from running the tests

    Note
    ----
    Its up to the calle of this function to assure that the tests and the
    python files are in the correct place.

    This function will create a python file `__test_executor.py` which will be
    running all the tests. This is because if we don't run the tests in a
    separate instance of python we will clutter up the imports and namespace
    of this python instance.
    """

    executor = run_directory/"__test_executor.py"

    with open(executor, "w") as f:
        f.write(_generate_executer())

    python_command = sys.executable

    proc = subprocess.run(
        [python_command, str(executor), str(run_directory)],
        cwd=str(run_directory),
        capture_output=True
    )

    return TestResults(**json.loads(proc.stdout))
