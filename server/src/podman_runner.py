import subprocess
import sys
from pathlib import Path

subprocess.run(["podman", "build", "-t", "podman_test_executor", "."])

proc = subprocess.run(["podman", "create", "podman_test_executor"],text=True, capture_output=True)
id = proc.stdout.removesuffix("\n")
test_files = Path(__file__).absolute().parent.parent/"Test"/"test_files_test_runner"


my_file = (test_files/"my_test_file.py").absolute()
test_0 = (test_files/"test_0.py").absolute()
test_1 = (test_files/"test_1.py").absolute()

subprocess.run(["podman", "cp", f"{str(test_0)}",  f"{id}:/DATX11/{test_0.name}"])
subprocess.run(["podman", "cp", f"{str(test_1)}",  f"{id}:/DATX11/{test_1.name}"])
subprocess.run(["podman", "cp", f"{str(my_file)}",  f"{id}:/DATX11/{my_file.name}"])


subprocess.run(["podman", "start","--attach", id])