from src.user_handler import get_courses
import sys
from pathlib import Path
import unittest
from unittest.mock import MagicMock, patch
from psycopg2 import IntegrityError

sys.path.append(str(Path(__file__).absolute().parent.parent))


class TestFileHandler(unittest.TestCase):
    def setup(self):
        self.test_file_dir = Path(__file__).parent/"test_files_user_handler"

