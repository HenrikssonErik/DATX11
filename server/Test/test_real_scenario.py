if False:
    from werkzeug.datastructures import FileStorage
    from io import BytesIO
    import sys
    import unittest
    from pathlib import Path
    sys.path.append(str(Path(__file__).absolute().parent.parent))
    from src.file_handler import run_unit_tests_in_container, \
                                    save_test_to_db, \
                                    save_assignment_to_db, \
                                    remove_existing_test_file, \
                                    handle_files, \
                                    get_assignment_test_feedback_from_database  # noqa : E402

    class TestRealRunUnitTestsInContainer(unittest.TestCase):
        """Test to make sure that tests are being executed in a container
        without any errors"""

        def setUp(self):
            self.test_file_dir = Path(__file__).parent/"test_files_test_runner"

        def test_run_unit_tests_in_container_successful(self):
            # Set up test data
            course_id = 6
            assignment = 1
            group_id = 1

            with open(self.test_file_dir/"test_1.py", "rb") as fp:
                file = FileStorage(BytesIO(fp.read()), filename="test_1.py")
            save_test_to_db(file, course_id, assignment)

            file_data = (self.test_file_dir/"my_test_file.py").read_bytes()

            save_assignment_to_db(
                "my_test_file.py",
                file_data,
                group_id,
                course_id,
                assignment
            )

            # Call function under test
            result_json = run_unit_tests_in_container(course_id, assignment,
                                                      group_id)

            # Clean up
            remove_existing_test_file("test_test_1.py", course_id, assignment)

            # Assert results
            self.assertTrue('"tests_run": 4' in result_json)
            self.assertTrue('"was_successful": true' in result_json)

        def test_run_unit_tests_in_container_fail(self):
            # Set up test data
            course_id = 6
            assignment = 1
            group_id = 1

            with open(self.test_file_dir/"test_0.py", "rb") as fp:
                file = FileStorage(BytesIO(fp.read()), filename="test_0.py")
            save_test_to_db(file, course_id, assignment)

            with open(self.test_file_dir/"test_1.py", "rb") as fp:
                file = FileStorage(BytesIO(fp.read()), filename="test_1.py")
            save_test_to_db(file, course_id, assignment)

            file_data = (self.test_file_dir/"my_test_file.py").read_bytes()

            save_assignment_to_db(
                "my_test_file.py",
                file_data,
                group_id,
                course_id,
                assignment
            )

            # Call function under test
            result_json = run_unit_tests_in_container(course_id, assignment,
                                                      group_id)

            # Clean up
            remove_existing_test_file("test_test_0.py", course_id, assignment)
            remove_existing_test_file("test_test_1.py", course_id, assignment)

            # Assert results
            self.assertTrue('"tests_run": 10' in result_json)
            self.assertTrue('"was_successful": false' in result_json)

    class TestFileHandler(unittest.TestCase):
        def setUp(self):
            self.test_file_dir = Path(__file__).parent/"test_files_test_runner"

        def test_handle_file_successful(self):
            course_id = 6
            assignment = 1
            group_id = 1
            # upload test files

            with open(self.test_file_dir/"test_1.py", "rb") as fp:
                file = FileStorage(BytesIO(fp.read()), filename="test_1.py")
            save_test_to_db(file, course_id, assignment)

            # upload my submision
            files = []
            with open(self.test_file_dir/"my_test_file.py", "rb") as fp:
                files.append(
                    FileStorage(
                        BytesIO(fp.read()),
                        filename="my_test_file.py"
                    )
                )

            handle_files(files, course_id, assignment, group_id)

            (all_feedback, code) = get_assignment_test_feedback_from_database(
                course_id, assignment, group_id
            )

            # clean up test files
            remove_existing_test_file("test_test_1.py", course_id, assignment)

            # clean up TotalFeedback

            # assert results
            self.assertTrue(all_feedback[-1][2])
