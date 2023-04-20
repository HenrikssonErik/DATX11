from pathlib import Path
import sys
import subprocess
import shutil


def test_runner(run_directory: Path) -> str:
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

    executor = Path(__file__).parent/"podman_test_executer.py"
    executor_copy = str(executor) if \
        (run_directory.parent/"podman_test_executer.py").exists() \
        else shutil.copy(executor, run_directory.parent)

    python_command = sys.executable

    proc = subprocess.run(
        [python_command, str(executor_copy)],
        cwd=str(run_directory),
        capture_output=True,
        text=True
    )
    return proc.stdout
