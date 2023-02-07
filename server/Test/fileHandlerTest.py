import sys

#import no working
sys.path.append('../server')

import unittest
from src.fileHandler import handle_files

class TestStringMethods(unittest.TestCase):

    def test_send_PDF_file(self):
        self.assertEqual(handle_files("Test1.pdf")[1], 200)


if __name__ == '__main__':
    unittest.main()