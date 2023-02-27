import subprocess
import os
from pathlib import Path


def gen_requirements(path: str):
    """
    Generates a requirements.txt in a given path
    Variables:
    path: Absolute path for directory
    """
    cmd = ["pipreqs", "--force", path]
    subprocess.run(cmd)


def copy_files(path: str, container_id: str):
    """Copies all files in a given directory to a created container
    path: Absolute path for directory
    container_id: Specifies container
    """
    for file_name in os.listdir(path):
        print(file_name)
        cmd = ["podman", "cp", f"{path}/{file_name}",
               f"{container_id}:/DATX11/{file_name}"]
        subprocess.run(cmd)


# This is to be changed, temporary poc
test_files = str(Path(__file__).absolute().parent/"test_files_test_runner")
gen_requirements(test_files)
subprocess.run(["podman", "build", "-t", "podman_test_executor", "."])
proc = subprocess.run(["podman", "create", "podman_test_executor"],
                      text=True, capture_output=True)
id = proc.stdout.removesuffix("\n")
copy_files(test_files, id)
subprocess.run(["podman", "start", "--attach", id])