
from src.
import sys
from pathlib import Path
import unittest
from unittest.mock import MagicMock, patch
from psycopg2 import IntegrityError

sys.path.append(str(Path(__file__).absolute().parent.parent))

class TestFileHandler(unittest.TestCase):
    
    def test_get_courses(self):
        id = 1
        get_courses(1)
