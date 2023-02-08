
import unittest
from src.fileHandler import handle_files

class TestStringMethods(unittest.TestCase):

    def test_send_PDF_file(self):
        files=[open("Test1.pdf")]
        self.assertEqual(handle_files(files)[1], 200)

    def test_send_txt_file(self):
        files=[open("test2.txt")]
        self.assertEqual(handle_files(files)[1], 200)
    
    def test_send_PY_file(self):
        files=[open("fileHandlerTest.py")]
        self.assertEqual(handle_files(files)[1], 200)

    def test_send_multiple_files(self):
        files = [open("Test1.pdf"), open("test2.txt"),open("fileHandlerTest.py")]
        self.assertEqual(handle_files(files)[1], 406) #only allows one file at the moment


if __name__ == '__main__':
    unittest.main()