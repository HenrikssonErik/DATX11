import sys
from pathlib import Path
import unittest
from unittest import mock
from werkzeug.datastructures import FileStorage
from io import BytesIO
from unittest.mock import MagicMock, patch

sys.path.append(str(Path(__file__).absolute().parent.parent))

from src.file_handler import handle_files, handle_test_file  # noqa: E402


def setup_mock_cursor(mock_connect) -> MagicMock:
    mock_cursor = MagicMock()
    mock_conn = MagicMock()
    mock_connect.return_value = mock_conn
    mock_conn.cursor.return_value.__enter__.return_value = mock_cursor

    return mock_cursor


filenames = ('PythonFile.py', 'Test1.pdf', 'test2.txt')


class TestFileHandler(unittest.TestCase):
    def setUp(self):
        self.test_file_dir = Path(__file__).parent/"test_files_file_handler"
        self.course_id = 1
        self.assignment = 1
        self.group_id = 1


    @patch('psycopg2.connect')
    def test_send_pdf_file(self, mock_connect):
        mock_cursor = setup_mock_cursor(mock_connect)
        mock_cursor.fetchall.return_value = (('Test1.pdf', ),)

        with open(self.test_file_dir/"Test1.pdf", "rb") as fp:
            file = FileStorage(BytesIO(fp.read()), filename="Test1.pdf")

        files = [file]
        self.assertEqual(handle_files(files, self.course_id,
                         self.group_id, self.assignment)[3], 200)

    @patch('psycopg2.connect')
    def test_send_txt_file(self, mock_connect):
        mock_cursor = setup_mock_cursor(mock_connect)
        mock_cursor.fetchall.return_value = (('test2.txt', ),)
        with open(self.test_file_dir/"test2.txt", "rb") as fp:
            file = FileStorage(BytesIO(fp.read()), filename="test2.txt")

        files = [file]
        self.assertEqual(handle_files(files, self.course_id,
                         self.group_id, self.assignment)[3], 200)

    @patch('psycopg2.connect')
    def test_send_py_file(self, mock_connect):
        mock_cursor = setup_mock_cursor(mock_connect)
        mock_cursor.fetchall.return_value = (('PythonFile.py', ),)
        with open(self.test_file_dir/"PythonFile.py", "rb") as fp:
            file = FileStorage(BytesIO(fp.read()), filename="PythonFile.py")

        files = [file]
        self.assertEqual(handle_files(files, self.course_id,
                         self.group_id, self.assignment)[3], 200)

    @patch('psycopg2.connect')
    def test_send_multiple_files(self, mock_connect):
        mock_cursor = setup_mock_cursor(mock_connect)
        mock_cursor.fetchall.return_value = (('Test1.pdf', ), ('test2.txt', ), ('pythonFile.py', ))
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
        self.assertEqual(handle_files(files, self.course_id,
                         self.group_id, self.assignment)[3], 406)

    @patch('psycopg2.connect')
    def test_send_pep8_checks_results(self, mock_connect):
        mock_cursor = setup_mock_cursor(mock_connect)
        mock_cursor.fetchall.return_value = (('PythonFile.py', ),)

        with open(self.test_file_dir/"PythonFile.py", "rb") as fp:
            file = FileStorage(BytesIO(fp.read()), filename="PythonFile.py")

        respons = handle_files([file], self.course_id,
                         self.group_id, self.assignment)
        self.assertEqual(respons[3], 200)
        self.assertEqual(respons[0][0]["PEP8_results"].count("F401"), 2)
        self.assertEqual(respons[0][0]["PEP8_results"].count("E401"), 1)

    @patch('psycopg2.connect')
    def test_send_py_test_file(self, mock_connect):
        mock_cursor = setup_mock_cursor(mock_connect)
        mock_cursor.fetchall.return_value = (('PythonFile.py', ),)
        with open(self.test_file_dir/"PythonFile.py", "rb") as fp:
            file = FileStorage(BytesIO(fp.read()), filename="PythonFile.py")

        files = [file]
        self.assertEqual(handle_test_file(
            files, self.course_id, self.assignment)[1], 200)

    # add test for uppload file?

    @patch('psycopg2.connect')
    def test_send_multiple_unit_test_files(self, mock_connect):
        mock_cursor = setup_mock_cursor(mock_connect)
        mock_cursor.fetchall.return_value = (('PythonFile.py', ), ('PythonFile.py', ))
        with open(self.test_file_dir/"PythonFile.py", "rb") as fp:
            file1 = FileStorage(BytesIO(fp.read()), filename="PythonFile.py")
        files = [file1]
        with open(self.test_file_dir/"PythonFile.py", "rb") as fp:
            file2 = FileStorage(BytesIO(fp.read()), filename="PythonFile.py")

        files.append(file2)
        self.assertEqual(handle_test_file(
            files, self.course_id, self.assignment)[1], 200)
    # add test for send in unittest


if __name__ == '__main__':
    unittest.main()
