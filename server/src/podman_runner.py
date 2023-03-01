import subprocess
from pathlib import Path


def gen_requirements(path: str):
    """
    Generates a requirements.txt in a given path
    --Parameters--
    path: Absolute path for directory
    """
    cmd = ["pipreqs", "--force", path]
    subprocess.run(cmd)


def copy_files(path: str, container_id: str):
    """Copies all files in a given directory to a created container
    --Parameters--
    path: Absolute path for directory
    container_id: Specifies container
    """
    cmd = ["podman", "cp", path, f"{container_id}:/"]
    subprocess.run(cmd)


def build_image(alias: str, directory: str):
    """
    Builds an image in a given directory
    --Parameters--
    alias: alias for the built image
    directory: Directory of the dockerfile, "." for current dir
    """
    subprocess.run(["podman", "build", "-t", alias, directory])


def create_image(alias: str):
    proc = subprocess.run(["podman", "create", alias],
                          text=True, capture_output=True)
    id = proc.stdout.removesuffix("\n")
    return id


# This is to be changed, temporary poc
test_files = str(Path(__file__).absolute().parent/"test_files_test_runner")
gen_requirements(test_files)
build_image("podman_test_executer", ".")
id = create_image("podman_test_executer")
copy_files(test_files, id)
subprocess.run(["podman", "start", "--attach", id])