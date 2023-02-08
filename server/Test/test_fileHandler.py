import sys
from pathlib import Path

sys.path.append(str(Path(__file__).absolute().parent.parent))

import unittest
from src.fileHandler import handle_files
from werkzeug.datastructures import FileStorage

class TestStringMethods(unittest.TestCase):

    def test_send_PDF_file(self):
        with open(Path(__file__).absolute().parent/"Test1.pdf", "rb") as fp:
            file = FileStorage(fp, filename="Test1.pdf")
        files=[file]
        self.assertEqual(handle_files(files)[1], 200)

    def test_send_txt_file(self):
        with open(Path(__file__).absolute().parent/"test2.txt", "rb") as fp:
            file = FileStorage(fp, filename="test2.txt")
        files=[file]
        self.assertEqual(handle_files(files)[1], 200)
    
    def test_send_PY_file(self):
        with open(Path(__file__).absolute().parent/"PythonFile.py", "rb") as fp:
            file = FileStorage(fp, filename="PythonFile.py")
        files=[file]
        self.assertEqual(handle_files(files)[1], 200)

    def test_send_multiple_files(self):
        files=[]
        with open(Path(__file__).absolute().parent/"Test1.pdf", "rb") as fp:
            file = FileStorage(fp, filename="Test1.pdf")
            files.append(file)
        with open(Path(__file__).absolute().parent/"test2.txt", "rb") as fp:
            file = FileStorage(fp, filename="test2.txt")
            files.append(file)
        
        with open(Path(__file__).absolute().parent/"PythonFile.py", "rb") as fp:
            file = FileStorage(fp, filename="PythonFile.py")
            files.append(file)
        print(len(files))
        self.assertEqual(handle_files(files)[1], 406) #only allows one file at the moment


if __name__ == '__main__':
    unittest.main()