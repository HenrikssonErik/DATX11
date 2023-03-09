import sys
from pathlib import Path
import unittest
from unittest.mock import Mock, patch
import bcrypt


sys.path.append(str(Path(__file__).absolute().parent.parent))
from src.login_handler import log_in, verify_token, create_token


class TestFileHandler(unittest.TestCase):

    def setUp(self):
        self.test_file_dir = Path(__file__).parent/"test_files_file_handler"

    @patch('app.psycopg2.connect')
    def test_log_in(self, mock_connect):
        with patch('psycopg2.connect') as mock_connect:
            # Set up the mock return value
            salt = bcrypt.gensalt()
            passphrase = bcrypt.hashpw('pass'.encode('utf8'), salt)
            mock_cursor = Mock(name='cursor')
            mock_cursor.fetchone.return_value = [1, passphrase]
            mock_conn = Mock(name='connection')
            mock_conn.cursor.return_value = mock_cursor
            mock_connect.return_value = mock_conn

            res = log_in('test1.chalmers.se', 'pass')
            print(res)
