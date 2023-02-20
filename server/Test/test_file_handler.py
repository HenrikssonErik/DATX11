import sys
from pathlib import Path
import unittest
from werkzeug.datastructures import FileStorage
from io import BytesIO

sys.path.append(str(Path(__file__).absolute().parent.parent))
from src.file_handler import handle_files  # noqa: E402


class TestFileHandler(unittest.TestCase):

    def setUp(self):
        self.test_file_dir = Path(__file__).parent/"test_files_file_handler"

    def test_send_pdf_file(self):
        with open(self.test_file_dir/"Test1.pdf", "rb") as fp:
            file = FileStorage(BytesIO(fp.read()), filename="Test1.pdf")

        files = [file]
        self.assertEqual(handle_files(files)[1], 200)

    def test_send_txt_file(self):
        with open(self.test_file_dir/"test2.txt", "rb") as fp:
            file = FileStorage(BytesIO(fp.read()), filename="test2.txt")

        files = [file]
        self.assertEqual(handle_files(files)[1], 200)

    def test_send_py_file(self):
        with open(self.test_file_dir/"PythonFile.py", "rb") as fp:
            file = FileStorage(BytesIO(fp.read()), filename="PythonFile.py")

        files = [file]
        self.assertEqual(handle_files(files)[1], 200)

    def test_send_multiple_files(self):
        files = []
        with open(self.test_file_dir/"Test1.pdf", "rb") as fp:
            file = FileStorage(BytesIO(fp.read()), filename="Test1.pdf")
            files.append(file)
        with open(self.test_file_dir/"test2.txt", "rb") as fp:
            file = FileStorage(BytesIO(fp.read()), filename="test2.txt")
            files.append(file)

        with open(self.test_file_dir/"PythonFile.py", "rb") as fp:
            file = FileStorage(BytesIO(fp.read()), filename="PythonFile.py")
            files.append(file)

        # only allows one file at the moment
        self.assertEqual(handle_files(files)[1], 406)

    def test_send_pep8_checks_results(self):
        with open(self.test_file_dir/"PythonFile.py", "rb") as fp:
            file = FileStorage(BytesIO(fp.read()), filename="PythonFile.py")

        respons = handle_files([file])

        self.assertEqual(respons[1], 200)
        self.assertEqual(respons[0]["PEP8_results"].count("F401"), 2)
        self.assertEqual(respons[0]["PEP8_results"].count("E401"), 1)


if __name__ == '__main__':
    unittest.main()
