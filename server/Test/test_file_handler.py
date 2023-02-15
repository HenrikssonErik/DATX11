import sys
from pathlib import Path
import unittest
from werkzeug.datastructures import FileStorage

sys.path.append(str(Path(__file__).absolute().parent.parent))
from src.file_handler import handle_files  # noqa: E402


class TestStringMethods(unittest.TestCase):

    def setUp(self):
        self.test_file_dir = Path(__file__).parent/"test_files_file_handler"

    def test_send_pdf_file(self):
        with open(self.test_file_dir/"Test1.pdf", "rb") as fp:
            file = FileStorage(fp, filename="Test1.pdf")

        files = [file]
        self.assertEqual(handle_files(files)[1], 200)

    def test_send_txt_file(self):
        with open(self.test_file_dir/"test2.txt", "rb") as fp:
            file = FileStorage(fp, filename="test2.txt")

        files = [file]
        self.assertEqual(handle_files(files)[1], 200)

    def test_send_py_file(self):
        with open(self.test_file_dir/"PythonFile.py", "rb") as fp:
            file = FileStorage(fp, filename="PythonFile.py")

        files = [file]
        self.assertEqual(handle_files(files)[1], 200)

    def test_send_multiple_files(self):
        files = []
        with open(self.test_file_dir/"Test1.pdf", "rb") as fp:
            file = FileStorage(fp, filename="Test1.pdf")
            files.append(file)
        with open(self.test_file_dir/"test2.txt", "rb") as fp:
            file = FileStorage(fp, filename="test2.txt")
            files.append(file)

        with open(self.test_file_dir/"PythonFile.py", "rb") as fp:
            file = FileStorage(fp, filename="PythonFile.py")
            files.append(file)

        # only allows one file at the moment
        self.assertEqual(handle_files(files)[1], 406)


if __name__ == '__main__':
    unittest.main()
