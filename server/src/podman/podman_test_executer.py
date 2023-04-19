from pathlib import Path
import unittest
from unittest.runner import TextTestResult
import json

if __name__ == "__main__":
    class TestResultsWithSuccessful(TextTestResult):

        def __init__(self, *args, **kwargs):
            super(TestResultsWithSuccessful, self).__init__(*args, **kwargs)
            self.successes = []

        def addSuccess(self, test):  # noqa: N802
            super(TestResultsWithSuccessful, self).addSuccess(test)
            self.successes.append(test.id())

    # test_dir = sys.argv[1]
    test_dir = str(Path(__file__).absolute().parent/"temp")

    test_suit = unittest.TestLoader().discover(
        test_dir, pattern="test_*.py"
    )
    # results = test_suit.run(unittest.TestResult(verbosity=2))
    results = unittest.runner.TextTestRunner(
        resultclass=TestResultsWithSuccessful
    ).run(test_suit)

    json_result = {
        "tests_run": results.testsRun,
        "was_successful": results.wasSuccessful(),
        "successes": results.successes,
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
