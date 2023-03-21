import unittest
from unittest.mock import MagicMock, patch
import sys
import os
import shutil
from io import BytesIO
from pathlib import Path
sys.path.append(str(Path(__file__).absolute().parent.parent))
from src.podman.podman_runner import gen_requirements, copy_files, \
                                     build_image, create_container, \
                                     run_container  # noqa: E402
from src.file_handler import run_unit_tests_in_container # noqa : E402


class TestGenRequirements(unittest.TestCase):
    def setUp(self):
        self.test_dir = os.path.join(os.path.dirname(__file__), 'test_dir')
        os.makedirs(self.test_dir, exist_ok=True)
    
    def test_gen_requirements(self):
        gen_requirements(self.test_dir)
        self.assertTrue(os.path.exists(os.path.join(self.test_dir,
                                                    'requirements.txt')))
    
    def tearDown(self):
        shutil.rmtree(self.test_dir)


class TestCopyFiles(unittest.TestCase):
    @patch('src.podman.podman_runner.subprocess.run')
    def test_copy_files(self, mock_subprocess):
        path = "/path/to/files"
        container_id = "container_id"
        
        # Mock the subprocess.run() function
        mock_subprocess.return_value = MagicMock()

        copy_files(path, container_id)

        # Check that the correct command was passed to subprocess.run()
        mock_subprocess.assert_called_once_with(
            ["podman", "cp", path, f"{container_id}:/"]
        )


class TestBuildImage(unittest.TestCase):
    @patch('src.podman.podman_runner.subprocess.run')
    def test_build_image(self, mock_subprocess):
        image_name = "test-image"
        directory = "/path/to/dockerfile"
        
        # Mock the subprocess.run() function
        mock_subprocess.return_value = MagicMock()

        build_image(image_name, directory)

        # Check that the correct command was passed to subprocess.run()
        mock_subprocess.assert_called_once_with(
            ["podman", "build", "-t", image_name, directory]
        )


class TestCreateContainer(unittest.TestCase):
    @patch('src.podman.podman_runner.subprocess.run')
    def test_create_container(self, mock_subprocess):
        image_name = "test-image"
        container_id = "container_id"
        
        # Mock the subprocess.run() function
        mock_subprocess.return_value = MagicMock()
        mock_subprocess.return_value.stdout = container_id

        id = create_container(image_name)

        # Check that the correct command was passed to subprocess.run()
        mock_subprocess.assert_called_once_with(
            ["podman", "create", image_name],
            text=True, capture_output=True
        )

        # Check that the correct container ID was returned
        self.assertEqual(id, container_id)


class TestRunContainer(unittest.TestCase):
    @patch('src.podman.podman_runner.create_container')
    @patch('src.podman.podman_runner.copy_files')
    @patch('src.podman.podman_runner.subprocess.run')
    def test_run_container(self, mock_subprocess, mock_copy_files,
                           mock_create_container):
        image_name = "test-image"
        test_dir = "/path/to/test/dir"
        container_id = "container_id"
        feedback = "{'results': 'pass'}"
        
        # Mock the create_container() function
        mock_create_container.return_value = container_id

        # Mock the copy_files() function
        mock_copy_files.return_value = None

        # Mock the subprocess.run() function
        mock_subprocess.return_value = MagicMock()
        mock_subprocess.return_value.stdout = feedback

        json_feedback = run_container(image_name, test_dir)
        """
        Check that the correct commands were passed
        to the subprocess.run() function
        """
        expected_commands = [
            ["podman", "start", "--attach", container_id],
            ["podman", "rmi", "-f", image_name]
        ]
        actual_commands = [args[0] for args,
                           kwargs in mock_subprocess.call_args_list]
        self.assertEqual(actual_commands, expected_commands)

        # Check that the correct feedback was returned
        self.assertEqual(json_feedback, feedback)


class TestRunUnitTestsInContainer(unittest.TestCase):
    @patch("src.file_handler.get_unit_test_files_from_db", 
           return_value=[("test_file.py", BytesIO(b" "))])
    @patch("src.file_handler.get_all_assignment_files_from_db",
           return_value=[("assignment_file.py", BytesIO(b" "))])
    @patch("src.file_handler.gen_requirements")
    @patch("src.file_handler.build_image")
    @patch("src.file_handler.run_container", return_value="{'status': 'OK'}")
    def test_run_unit_tests_in_container(
        self
    ):
        # Set up test data
        courseid = 123
        assignment = 1
        group_id = 456
        expected_json = "{'status': 'OK'}"

        # Call function under test
        result_json = run_unit_tests_in_container(courseid, assignment,
                                                  group_id)
        # Assert results
        self.assertEqual(result_json, expected_json)