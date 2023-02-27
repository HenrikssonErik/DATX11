import subprocess
import os
from pathlib import Path


def gen_requirements(path: str):
    cmd = ["pipreqs", "--force", path]
    subprocess.run(cmd)


def copy_files(path: str, id: str):
    for name in os.listdir(path):
        print(name)
        cmd = ["podman", "cp", f"{path}/{name}", f"{id}:/DATX11/{name}"]
        subprocess.run(cmd)


test_files = str(Path(__file__).absolute().parent/"test_files_test_runner")
gen_requirements(test_files)
subprocess.run(["podman", "build", "-t", "podman_test_executor", "."])
proc = subprocess.run(["podman", "create", "podman_test_executor"],
                      text=True, capture_output=True)
id = proc.stdout.removesuffix("\n")
copy_files(test_files, id)


subprocess.run(["podman", "start", "--attach", id])