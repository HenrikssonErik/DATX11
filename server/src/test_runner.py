from pathlib import Path
import sys
import shutil
import subprocess
import json
from dataclasses import dataclass

@dataclass
class TestResults:
    """
    A dataclass to store the results of the tests that have been run.
    """
    testsRun: int
    wasSuccessful: bool
    errors: list[tuple[str, str]]
    failures: list[tuple[str, str]]
    expectedFailures: list[tuple[str, str]]
    unexpectedSuccesses: list[str]
    skipped: list[tuple[str, str]]



def test_runner(file: Path, tests: list[Path], run_directory: Path) -> TestResults:
    """
    This function copy's the `file` and `tests` to the `run_directory` and starts another 
    instance of python which will execute the test. This is done so we dont clutter up the 
    namespace of the main instance.
    After the new instance is started, it will start to gather all the test in to a test suit.
    Then the tests are run and the result is returned back.

    Takes in:
        file: `pathlib.Path` to the file which should be tested.
        tests: `list[pathlib.Path]` to the test files which should be run on the file.
        run_directory: `pathlib.Path` to the directory where the file will be tested with 
        the given tests.

    Returns: a `TestResults` which is where the results of the tests is stored.

    Note:
    Currently it is up to the calle to ensure that the run_directory does not have any files 
    of the same names as the the `file` or `tests`.
    """
    
    executor = Path(__file__).parent/"test_executor.py"
    test_dir = run_directory/"test_dir"

    test_dir.mkdir()
    executor_copy = shutil.copy(str(executor), run_directory)
    shutil.copy(str(file.absolute()), test_dir)

    for test in tests:
        shutil.copy(str(test.absolute()), test_dir)


    PYTHON_COMMAND = sys.executable

    proc = subprocess.run([PYTHON_COMMAND, str(executor_copy), str(test_dir)], cwd=str(run_directory), capture_output=True)

    
    return TestResults(**json.loads(proc.stdout))

