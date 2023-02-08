import sys
from pathlib import Path

sys.path.append(str(Path(__file__).absolute().parent.parent))

import unittest
from src.fileHandler import handle_files
from src.app import post_files

class TestStringMethods(unittest.TestCase):

    def test_send_PDF_file(self):
        files=[File("Test1.pdf")]
        self.assertEqual(handle_files(files)[1], 200)

    def test_send_txt_file(self):
        files=[File("test2.txt")]
        self.assertEqual(handle_files(files)[1], 200)
    
    def test_send_PY_file(self):
        files=[File("fileHandlerTest.py")]
        self.assertEqual(handle_files(files)[1], 200)

    def test_send_multiple_files(self):
        files = [File("Test1.pdf"), File("test2.txt"), File("fileHandlerTest.py")]
        self.assertEqual(handle_files(files)[1], 406) #only allows one file at the moment

    def test_post_no_files(self):
        self.assertEqual(post_files()[1],406)

class File:
    filename:str

    def __init__(name:str):
        filename = name

if __name__ == '__main__':
    unittest.main()