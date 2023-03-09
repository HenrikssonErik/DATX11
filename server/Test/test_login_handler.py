import sys
from pathlib import Path
import unittest
from unittest import mock

sys.path.append(str(Path(__file__).absolute().parent.parent))
from src.login_handler import   # noqa: E402


@mock.patch("psycopg2.connect")
class TestFileHandler(unittest.TestCase):

    def setUp(self):
        self.test_file_dir = Path(__file__).parent/"test_files_file_handler"