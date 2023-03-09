from src.login_handler import log_in, verify_token, create_token, createKey, check_data_input
import sys
from pathlib import Path
import unittest
from unittest.mock import MagicMock, patch
import bcrypt

sys.path.append(str(Path(__file__).absolute().parent.parent))


class TestFileHandler(unittest.TestCase):

    def setUp(self):
        self.test_file_dir = Path(__file__).parent/"test_files_file_handler"
        createKey()

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
    def test_user_registration(self, mock_connect):
        print("Yo")

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

    @patch('psycopg2.connect')
    def test_unsucessfull_log_in(self, mock_connect):
        # Set up the mock return value
        salt = bcrypt.gensalt()
        passphrase = memoryview(bcrypt.hashpw('pass'.encode('utf8'), salt))
        mock_cursor = MagicMock()
        mock_conn = MagicMock()
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
        mock_cursor.fetchone.return_value = [1, passphrase]

        result = log_in('test1.chalmers.se', 'pass1')
        self.assertEqual(result[1], 401)
        self.assertEqual(result[0], ("Wrong Credentials"))

    def test_create_and_verify_token(self):
        token = create_token(2)
        verify_token(token.get('Token'))
