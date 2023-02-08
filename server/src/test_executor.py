import unittest
import json
import sys

# This script should be started in a new instance of python and then will 
# print the tests results to stdout in a json format
if __name__ == "__main__":
    test_dir = sys.argv[1]
    test_suit = unittest.TestLoader().discover(test_dir, pattern="test_*.py")
    results = test_suit.run(unittest.TestResult(verbosity=2))
    json_result = {
        "testsRun": results.testsRun,
        "wasSuccessful": results.wasSuccessful(),
        "errors": [(e[0].id(), e[1]) for e in results.errors],
        "failures": [(e[0].id(), e[1]) for e in results.failures],
        "expectedFailures": [(e[0].id(), e[1]) for e in results.expectedFailures],
        "unexpectedSuccesses": [e.id() for e in results.unexpectedSuccesses],
        "skipped": [(e[0].id(), e[1]) for e in results.skipped],
    }

    print(json.dumps(json_result))
        