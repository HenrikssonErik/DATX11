from src.login_handler import log_in, verify_and_get_token, create_token, \
    create_key, check_data_input, user_registration, registration_query
import sys
from pathlib import Path
import unittest
from unittest.mock import MagicMock, patch
import bcrypt
from psycopg2 import IntegrityError


sys.path.append(str(Path(__file__).absolute().parent.parent))


def setup_mock_cursor(mock_connect) -> MagicMock:
    """Mocks the cursor to the mocked connection, which executes the sql query
    to the mock connection."""
    mock_cursor = MagicMock()
    mock_conn = MagicMock()
    mock_connect.return_value = mock_conn
    mock_conn.cursor.return_value.__enter__.return_value = mock_cursor

    return mock_cursor


class TestLoginHandler(unittest.TestCase):

    def setUp(self):
        self.test_file_dir = Path(__file__).parent/"test_files_file_handler"
        create_key()

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
    def test_user_registration_success(self, mock_connect):
        with patch.object(bcrypt, 'gensalt') as mock_gensalt:
            mock_gensalt.return_value = b'$2b$12$5OYDyM.lB5wBLwMhFJj42O'
            salt = bcrypt.gensalt()
            passphrase = memoryview(bcrypt.hashpw('abc123'.encode('utf8'),
                                                  salt))
            mock_cursor = setup_mock_cursor(mock_connect)
            mock_cursor.fetchone.return_value = [1, passphrase]

            result = user_registration({'cid': 'abc',
                                        'email': 'abc@chalmers.se',
                                        'password': 'abc123'})

            self.assertEqual(result[1], 200)
            self.assertTrue(result[0].get('Token').
                            startswith("eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9"))

    @patch('psycopg2.connect')
    def test_registration_query_success(self, mock_connect):
        mock_cursor = setup_mock_cursor(mock_connect)

        cid = 'abc'
        email = 'abc@example.com'
        hashed_pass = b'secret'

        result = registration_query(cid, email, hashed_pass)
        mock_cursor.execute.assert_called_once_with("""INSERT INTO UserData
                (cid, email, passphrase)
                VALUES (%s, %s, %s);""", (cid, email, hashed_pass))

        self.assertEqual(result, ({'status': 'success'}, 200))

    @patch('psycopg2.connect')
    def test_registration_query_unique_key_exception(self, mock_connect):
        mock_cursor = setup_mock_cursor(mock_connect)
        mock_cursor.execute.side_effect = IntegrityError(
            "duplicate key value violates unique constraint 'userdata_pkey'"
        )

        cid = 'abc'
        email = 'abc@example.com'
        hashed_pass = b'secret'

        result = registration_query(cid, email, hashed_pass)

        mock_cursor.execute.assert_called_once_with("""INSERT INTO UserData
                (cid, email, passphrase)
                VALUES (%s, %s, %s);""", (cid, email, hashed_pass))

        self.assertEqual(result, ({'status': 'already_registered'}, 406))

    @ patch('psycopg2.connect')
    def test_sucessful_log_in(self, mock_connect):
        # Set up the mock return value
        salt = bcrypt.gensalt()
        passphrase = memoryview(bcrypt.hashpw('pass'.encode('utf8'), salt))
        mock_cursor = setup_mock_cursor(mock_connect)
        mock_cursor.fetchone.return_value = [1, passphrase]
        result = log_in('test1.chalmers.se', 'pass')
        self.assertEqual(result[1], 200)
        self.assertTrue(result[0].get('Token').startswith(
            'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9'))

    @ patch('psycopg2.connect')
    def test_unsucessful_log_in(self, mock_connect):
        # Set up the mock return value
        salt = bcrypt.gensalt()
        passphrase = memoryview(bcrypt.hashpw('pass'.encode('utf8'), salt))
        mock_cursor = setup_mock_cursor(mock_connect)
        mock_cursor.fetchone.return_value = [1, passphrase]

        result = log_in('test1.chalmers.se', 'pass1')
        self.assertEqual(result[1], 401)
        self.assertEqual(result[0].get('status'), ("wrong_credentials"))

    def test_create_and_verify_token(self):
        token = create_token(2)
        verify_and_get_token(token.get('Token'))
