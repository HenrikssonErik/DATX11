import subprocess
# from pathlib import Path


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


def build_image(image_name: str, directory: str):
    """
    Builds an image in a given directory
    --Parameters--
    alias: alias for the built image
    directory: Directory of the dockerfile, "." for current dir
    """
    subprocess.run(["podman", "build", "-t", image_name, directory])


def create_container(image_name: str) -> str:
    """
    creates a container from a given image name
    """
    proc = subprocess.run(["podman", "create", image_name],
                          text=True, capture_output=True)
    id = proc.stdout.removesuffix("\n")
    return id


def run_container(image_name: str, test_dir: str) -> str:
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
    subprocess.run(["podman", "rmi", "-f", image_name])
    return proc.stdout
