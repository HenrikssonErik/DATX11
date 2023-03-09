import sys
from pathlib import Path
import unittest
from unittest.mock import MagicMock, patch
import bcrypt


sys.path.append(str(Path(__file__).absolute().parent.parent))
from src.login_handler import log_in, verify_token, create_token, createKey


class TestFileHandler(unittest.TestCase):

    def setUp(self):
        self.test_file_dir = Path(__file__).parent/"test_files_file_handler"
        createKey()

    @patch('psycopg2.connect')
    def test_sucessfull_log_in(self, mock_connect):
        # Set up the mock return value
        salt = bcrypt.gensalt()
        passphrase = memoryview(bcrypt.hashpw('pass'.encode('utf8'), salt))
        mock_cursor = MagicMock()
        mock_conn = MagicMock()
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
        mock_cursor.fetchone.return_value = [1, passphrase]

        result = log_in('test1.chalmers.se', 'pass')
        self.assertEqual(result[1], 200)
        self.assertTrue(result[0].get('Token').startswith('eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9'))
