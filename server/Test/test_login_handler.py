import sys
from pathlib import Path
import unittest
from unittest.mock import Mock, patch
import bcrypt
from src.login_handler import log_in, check_data_input

sys.path.append(str(Path(__file__).absolute().parent.parent))


class TestFileHandler(unittest.TestCase):

    def setUp(self):
        self.test_file_dir = Path(__file__).parent/"test_files_file_handler"

    def test_check_data_input(self):
        # Test case where input data is valid
        self.assertEqual(check_data_input(
            'abc', 'abc@chalmers.se', '1234'), ('OK', 200))

        # Test case where cid contains invalid characters
        self.assertEqual(check_data_input(
            '123', 'abc@chalmers.se', '1234'), ('unallowed_tokens', 400))

        # Test case where email is missing
        self.assertEqual(check_data_input(
            'abc', '', '1234'), ('email_missing', 400))

        # Test case where email format is wrong
        self.assertEqual(check_data_input(
            'abc', 'def@chalmers.se', '1234'), ('wrong_format', 400))

        # Test case where password contains invalid characters
        self.assertEqual(check_data_input(
            'abc', 'abc@chalmers.se', 'أَلِف'), ('pass_not_ok', 400))

    @patch('psycopg2.connect')
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
