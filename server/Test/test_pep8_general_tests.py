import shutil
import tempfile
import unittest
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).absolute().parent.parent))

from src.general_tests import pep8_check   # noqa: E402


def move_test_file(file: str | Path, dir: str | Path):
    f = Path(file)
    d = Path(dir)
    shutil.copy(f, d)


class TestPEP8CheckNoConfig(unittest.TestCase):
    def setUp(self):
        self.tmp_dir = tempfile.TemporaryDirectory(
            suffix="__PEP8Check"
        )
        self.current_dir = Path(__file__).parent
        self.tmp_dir_path = Path(self.tmp_dir.name)
        self.test_file_dir = \
            Path(__file__).parent/"test_files_pep8_general_test"

    def tearDown(self):
        self.tmp_dir.cleanup()

    def test_pep8_check_good(self):
        move_test_file(self.test_file_dir/"good.py", self.tmp_dir_path)

        result = pep8_check(self.tmp_dir_path)
        self.assertEqual(len(result), 0)

    def test_pep8_check_import_bad(self):
        move_test_file(self.test_file_dir/"import_bad.py", self.tmp_dir_path)

        result = pep8_check(self.tmp_dir_path)

        self.assertEqual(result.count("E401"), 1)

    def test_pep8_check_functions_to_close_bad(self):
        move_test_file(
            self.test_file_dir/"functions_to_close_bad.py", self.tmp_dir_path
        )

        result = pep8_check(self.tmp_dir_path)

        self.assertEqual(result.count("E302"), 1)

    def test_pep8_check_indentation_bad(self):
        move_test_file(
            self.test_file_dir/"indentation_bad.py", self.tmp_dir_path
        )

        result = pep8_check(self.tmp_dir_path)

        self.assertEqual(result.count("E111"), 2)


class TestPEP8CheckNoConfigFilenamePat(unittest.TestCase):
    def setUp(self):
        self.tmp_dir = tempfile.TemporaryDirectory(
            suffix="__PEP8Check"
        )
        self.current_dir = Path(__file__).parent
        self.tmp_dir_path = Path(self.tmp_dir.name)
        self.test_file_dir = \
            Path(__file__).parent/"test_files_pep8_general_test"

    def tearDown(self):
        self.tmp_dir.cleanup()

    def test_pep8_check_good_no_match(self):
        move_test_file(self.test_file_dir/"good.py", self.tmp_dir_path)

        result = pep8_check(self.tmp_dir_path, filename_patterns=["no_match"])
        self.assertEqual(len(result), 0)

    def test_pep8_check_good_match(self):
        move_test_file(self.test_file_dir/"good.py", self.tmp_dir_path)

        result = pep8_check(self.tmp_dir_path, filename_patterns=["./good.py"])
        self.assertEqual(len(result), 0)

    def test_pep8_check_import_bad_no_match(self):
        move_test_file(self.test_file_dir/"import_bad.py", self.tmp_dir_path)

        result = pep8_check(self.tmp_dir_path, filename_patterns=["no_match"])

        self.assertEqual(result.count("E401"), 0)

    def test_pep8_check_import_bad_match(self):
        move_test_file(self.test_file_dir/"import_bad.py", self.tmp_dir_path)

        result = pep8_check(self.tmp_dir_path, filename_patterns=[
                            "./import_bad.py"])

        self.assertEqual(result.count("E401"), 1)

    def test_pep8_check_functions_to_close_bad_no_match(self):
        move_test_file(
            self.test_file_dir/"functions_to_close_bad.py", self.tmp_dir_path
        )

        result = pep8_check(self.tmp_dir_path, filename_patterns=["no_match"])

        self.assertEqual(result.count("E302"), 0)

    def test_pep8_check_functions_to_close_bad_match(self):
        move_test_file(
            self.test_file_dir/"functions_to_close_bad.py", self.tmp_dir_path
        )

        result = pep8_check(
            self.tmp_dir_path,
            filename_patterns=[
                "./functions_to_close_bad.py"
            ]
        )

        self.assertEqual(result.count("E302"), 1)

    def test_pep8_check_indentation_bad_no_match(self):
        move_test_file(
            self.test_file_dir/"indentation_bad.py", self.tmp_dir_path
        )

        result = pep8_check(self.tmp_dir_path, filename_patterns=["no_match"])

        self.assertEqual(result.count("E111"), 0)

    def test_pep8_check_indentation_bad_match(self):
        move_test_file(
            self.test_file_dir/"indentation_bad.py", self.tmp_dir_path
        )

        result = pep8_check(
            self.tmp_dir_path, filename_patterns=["./indentation_bad.py"]
        )

        self.assertEqual(result.count("E111"), 2)

    def test_pep8_check_many_pats(self):
        move_test_file(
            self.test_file_dir/"indentation_bad.py", self.tmp_dir_path
        )
        move_test_file(
            self.test_file_dir/"import_bad.py", self.tmp_dir_path
        )
        move_test_file(
            self.test_file_dir/"functions_to_close_bad.py", self.tmp_dir_path
        )

        result = pep8_check(
            self.tmp_dir_path, filename_patterns=[
                "./indentation_bad.py", "./import_bad.py"
            ]
        )

        self.assertEqual(result.count("E111"), 2)
        self.assertEqual(result.count("E401"), 1)
        self.assertEqual(result.count("E302"), 0)


class TestPEP8CheckWithConfig(unittest.TestCase):
    def setUp(self):
        self.tmp_dir = tempfile.TemporaryDirectory(
            suffix="__PEP8Check"
        )
        self.tmp_dir_path = Path(self.tmp_dir.name)
        self.current_dir = Path(__file__).parent
        self.test_file_dir = \
            Path(__file__).parent/"test_files_pep8_general_test"

        self.config = self.tmp_dir_path/"test_config.ini"

    def tearDown(self):
        self.tmp_dir.cleanup()

    def test_pep8_check_good(self):
        with open(self.config, "w") as f:
            f.write("[flake8]\nstatistics = True")

        move_test_file(self.test_file_dir/"good.py", self.tmp_dir_path)

        result = pep8_check(self.tmp_dir_path, flake8_config=self.config)

        self.assertEqual(len(result), 0)

    def test_pep8_check_config_not_found(self):

        move_test_file(self.test_file_dir/"good.py", self.tmp_dir_path)

        with self.assertRaises(FileNotFoundError):
            pep8_check(self.tmp_dir_path, flake8_config=self.config)

    def test_pep8_check_import_bad(self):
        with open(self.config, "w") as f:
            f.write("[flake8]\nstatistics = True")

        move_test_file(self.test_file_dir/"import_bad.py", self.tmp_dir_path)

        result = pep8_check(self.tmp_dir_path, flake8_config=self.config)

        self.assertEqual(result.count("E401"), 2)

    def test_pep8_check_functions_to_close_bad(self):
        with open(self.config, "w") as f:
            f.write("[flake8]\nstatistics = True")
        move_test_file(
            self.test_file_dir/"functions_to_close_bad.py", self.tmp_dir_path
        )

        result = pep8_check(self.tmp_dir_path, flake8_config=self.config)

        self.assertEqual(result.count("E302"), 2)

    def test_pep8_check_indentation_bad(self):
        with open(self.config, "w") as f:
            f.write("[flake8]\nstatistics = True")
        move_test_file(
            self.test_file_dir/"indentation_bad.py", self.tmp_dir_path
        )

        result = pep8_check(self.tmp_dir_path, flake8_config=self.config)

        self.assertEqual(result.count("E111"), 3)
