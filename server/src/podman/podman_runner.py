import subprocess
import os
from pathlib import Path
__cached_images = {"default"}


def init_images(): 
    print("Got here ")
    cmd = ["podman", "build", "-t", "default",
           "-f", "Containerfile.basic", Path(__file__).absolute().parent]
    subprocess.run(cmd)


def gen_requirements(path: str) -> bool:
    """
    Generates a requirements.txt in a given path
    --Parameters--
    path: Absolute path for directory
    Returns true if no dependencies are needed
    """
    cmd = ["pipreqs", "--force", path]
    subprocess.run(cmd)
    return os.stat(f"{path}/requirements.txt").st_size == 1


def copy_files(path: str, container_id: str):
    """Copies all files in a given directory to a created container
    --Parameters--
    path: Absolute path for directory
    container_id: Specifies container
    """
    print(path)
    cmd = ["podman", "cp", path, f"{container_id}:/"]
    subprocess.run(cmd)


def build_image(image_name: str, directory: str):
    """
    Builds an image in a given directory
    --Parameters--
    alias: alias for the built image
    directory: Directory of the dockerfile, "." for current dir
    """
    subprocess.run(["podman", "build", "-t", image_name, "-f",
                    "Containerfile.general", directory])


def create_container(image_name: str) -> str:
    """
    creates a container from a given image name
    """
    proc = subprocess.run(["podman", "create", image_name],
                          text=True, capture_output=True)
    id = proc.stdout.removesuffix("\n")
    return id


def run_container(image_name: str, test_dir: str, is_empty: bool) -> str:
    """
    Creates and runs container but not started container and returns
    feedback from tests. Deletes image when feedback been received.
    --Parameters--
    image_name: Name of image to create and delete
    test_dir: Absolute path of test directory
    --Returns--
    str: unittest feedback in json string format
    """

    id = create_container(image_name)
    copy_files(test_dir, id)
    proc = subprocess.run(["podman", "start", "--attach", id],
                          text=True, capture_output=True)
    json_feedback = proc.stdout
    if (not is_empty):
        cmd = ["podman", "rmi", "-f", image_name]
        print("Deleting Image")
    else:
        print("Deleting container")
        cmd = ["podman", "rm", "-f", id]
    subprocess.run(cmd)
    return json_feedback