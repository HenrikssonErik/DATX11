import sys
from pathlib import Path
import unittest
from unittest import mock
from werkzeug.datastructures import FileStorage
from io import BytesIO
sys.path.append(str(Path(__file__).absolute().parent.parent))

from src.file_handler import handle_files, handle_test_file  # noqa: E402


@mock.patch("psycopg2.connect")
class TestFileHandler(unittest.TestCase):
    def setUp(self):
        self.test_file_dir = Path(__file__).parent/"test_files_file_handler"

        # use this to return data from mock db
        # result of psycopg2.connect(**connection_stuff)
        # mock_con = mock_connect.return_value

        # result of con.cursor(cursor_factory=DictCursor)
        # mock_cur = mock_con.cursor.return_value

        # return this when calling cur.fetchall()
        # mock_cur.fetchall.return_value = expected

    def test_send_pdf_file(self, mock_connect):

        with open(self.test_file_dir/"Test1.pdf", "rb") as fp:
            file = FileStorage(BytesIO(fp.read()), filename="Test1.pdf")

        files = [file]
        self.assertEqual(handle_files(files)[2], 200)

    def test_send_txt_file(self, mock_connect):
        with open(self.test_file_dir/"test2.txt", "rb") as fp:
            file = FileStorage(BytesIO(fp.read()), filename="test2.txt")

        files = [file]
        self.assertEqual(handle_files(files)[2], 200)

    def test_send_py_file(self, mock_connect):
        with open(self.test_file_dir/"PythonFile.py", "rb") as fp:
            file = FileStorage(BytesIO(fp.read()), filename="PythonFile.py")

        files = [file]
        self.assertEqual(handle_files(files)[2], 200)

    def test_send_multiple_files(self, mock_connect):
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
        self.assertEqual(handle_files(files)[2], 406)

    def test_send_pep8_checks_results(self, mock_connect):
        with open(self.test_file_dir/"PythonFile.py", "rb") as fp:
            file = FileStorage(BytesIO(fp.read()), filename="PythonFile.py")
    
        respons = handle_files([file])
        self.assertEqual(respons[2], 200)
        self.assertEqual(respons[0][0]["PEP8_results"].count("F401"), 2)
        self.assertEqual(respons[0][0]["PEP8_results"].count("E401"), 1)
        
    def test_send_py_test_file(self, mock_connect):
        with open(self.test_file_dir/"PythonFile.py", "rb") as fp:
            file = FileStorage(BytesIO(fp.read()), filename="PythonFile.py")

        files = [file]
        self.assertEqual(handle_test_file(files)[1], 200)

    # add test for uppload file?

    def test_send_multiple_unit_test_files(self, mock_connect):
        with open(self.test_file_dir/"PythonFile.py", "rb") as fp:
            file1 = FileStorage(BytesIO(fp.read()), filename="PythonFile.py")
        files = [file1]
        with open(self.test_file_dir/"PythonFile.py", "rb") as fp:
            file2 = FileStorage(BytesIO(fp.read()), filename="PythonFile.py")

        files.append(file2)
        self.assertEqual(handle_test_file(files)[1], 200)
    # add test for send in unittest


if __name__ == '__main__':
    unittest.main()
