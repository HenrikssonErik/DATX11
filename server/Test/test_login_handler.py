import random
import string
from typing import Literal
import sys
from pathlib import Path
import unittest
from unittest.mock import MagicMock, patch
import bcrypt
from psycopg2 import IntegrityError
import bcrypt
from unittest.mock import MagicMock, patch
import unittest
from pathlib import Path
import sys
from typing import Literal
import string
from random import random

sys.path.append(str(Path(__file__).absolute().parent.parent))
from src.login_handler import log_in, verify_and_get_id, create_token, create_key, check_data_input, user_registration, registration_query, create_verification_token, verify_user_in_db, verify_user_from_email_verification  # noqa: E402, E501


def setup_mock_cursor(mock_connect) -> MagicMock:
    """Mocks the cursor to the mocked connection, which executes the sql query
    to the mock connection."""
    mock_cursor = MagicMock()
    mock_conn = MagicMock()
    mock_connect.return_value = mock_conn
    mock_conn.cursor.return_value.__enter__.return_value = mock_cursor

    return mock_cursor


def random_cid_generator(length=6) -> str:
    random_cid = ''.join(random.choice(string.ascii_lowercase)
                         for i in range(length))
    return random_cid


class TestFileHandler(unittest.TestCase):
    def setUp(self):
        create_key()

    def test_check_data_input(self):
        # Test case where input data is valid
        self.assertEqual(check_data_input(
            'abc', 'abc@chalmers.se', '1234', True), ('OK', 200))

        # Test case where cid contains invalid characters
        self.assertEqual(check_data_input(
            '123', 'abc@chalmers.se', '1234', True), ('unallowed_tokens', 400))

        # Test case where email is missing
        self.assertEqual(check_data_input(
            'abc', '', '1234', True), ('email_missing', 400))

        # Test case where email format is wrong
        self.assertEqual(check_data_input(
            'abc', 'def@chalmers.se', '1234', True), ('wrong_format', 400))

        # Test case where password contains invalid characters
        self.assertEqual(check_data_input(
            'abc', 'abc@chalmers.se', 'أَلِف', True), ('pass_not_ok', 400))

    @patch('psycopg2.connect')
    def test_user_registration_success(self, mock_connect):
        with patch.object(bcrypt, 'gensalt') as mock_gensalt:
            mock_gensalt.return_value = b'$2b$12$5OYDyM.lB5wBLwMhFJj42O'
            salt = bcrypt.gensalt()
            passphrase = memoryview(bcrypt.hashpw('abc123'.encode('utf8'),
                                                  salt))
            mock_cursor = setup_mock_cursor(mock_connect)
            mock_cursor.fetchone.return_value = [1, passphrase, 'Admin']

            result = user_registration({'cid': 'erhen',
                                        'email': 'erhen@chalmers.se',
                                        'password': 'abc123'})

            self.assertEqual(result[1], 200)
            self.assertTrue(result[0].get('Token').
                            startswith("eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9"))

    @patch('psycopg2.connect')
    def test_registration_query_success(self, mock_connect):
        mock_cursor = setup_mock_cursor(mock_connect)

        random_cid = random_cid_generator()

        cid = random_cid
        email = cid + '@example.com'
        hashed_pass = b'secret'
        role = 'student'
        name = 'Test Testsson'

        result = registration_query(cid, email, hashed_pass, role, name)
        mock_cursor.execute.assert_called_once_with("""INSERT INTO UserData
                (cid, email, passphrase, globalRole, fullName)
                VALUES (%s, %s, %s, %s, %s );""", (cid, email, hashed_pass, role, name))

        self.assertEqual(result, ({'status': 'success'}, 200))

    @patch('psycopg2.connect')
    def test_registration_query_unique_key_exception(self, mock_connect):
        mock_cursor = setup_mock_cursor(mock_connect)
        mock_cursor.execute.side_effect = IntegrityError(
            "duplicate key value violates unique constraint 'userdata_pkey'"
        )

        random_cid = random_cid_generator()

        cid = random_cid
        email = cid + '@example.com'
        hashed_pass = b'secret'
        role = 'student'
        name = 'Test Testsson'

        result = registration_query(cid, email, hashed_pass, role, name)

        mock_cursor.execute.assert_called_once_with("""INSERT INTO UserData
                (cid, email, passphrase, globalRole, fullName)
                VALUES (%s, %s, %s, %s, %s );""", (cid, email, hashed_pass, role, name))

        self.assertEqual(result, ({'status': 'already_registered'}, 406))

    @ patch('psycopg2.connect')
    def test_sucessful_log_in(self, mock_connect):
        # Set up the mock return value
        salt = bcrypt.gensalt()
        passphrase = memoryview(bcrypt.hashpw('pass'.encode('utf8'), salt))
        mock_cursor = setup_mock_cursor(mock_connect)
        mock_cursor.fetchone.return_value = [1, passphrase, 'Admin']
        result = log_in('test1.chalmers.se', 'pass')
        self.assertEqual(result[1], 200)
        self.assertTrue(result[0].get('Token').startswith(
            'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9'))

    @patch('psycopg2.connect')
    def test_unsucessful_log_in(self, mock_connect):
        # Set up the mock return value
        salt = bcrypt.gensalt()
        passphrase = memoryview(bcrypt.hashpw('pass'.encode('utf8'), salt))
        mock_cursor = setup_mock_cursor(mock_connect)
        mock_cursor.fetchone.return_value = [1, passphrase, 'Admin']

        result = log_in('test1.chalmers.se', 'pass1')
        self.assertEqual(result[1], 401)
        self.assertEqual(result[0].get('status'), ("wrong_credentials"))

    def test_create_and_verify_id(self):
        token = create_token(2)
        verify_and_get_id(token)

    @patch('psycopg2.connect')
    def test_verify_user_in_db_success(self, mock_connect):
        mock_cur = setup_mock_cursor(mock_connect)
        mock_cur.rowcount = 1
        expected_tuple: tuple[dict[str, str], Literal[200]] = \
            {'status': 'success'}, 200

        random_cid = random_cid_generator()

        response = verify_user_in_db(random_cid)
        self.assertTupleEqual(
            tuple(expected_tuple), tuple(response))
        mock_cur.execute.assert_called_once_with("""UPDATE UserData
                SET verified = TRUE
                WHERE cid = %s""", (random_cid,))

    @patch('psycopg2.connect')
    def test_verify_user_in_db_no_user_updated_fail(self, mock_connect):
        mock_cur = setup_mock_cursor(mock_connect)
        mock_cur.rowcount = 0
        expected_tuple: tuple[dict[str, str], Literal[406]] = \
            {'status': 'no_user_to_verify'}, 406

        random_cid = random_cid_generator()

        response = verify_user_in_db(random_cid)

        self.assertTupleEqual(
            tuple(expected_tuple), tuple(response))
        mock_cur.execute.assert_called_once_with("""UPDATE UserData
                SET verified = TRUE
                WHERE cid = %s""", (random_cid,))

    @patch('psycopg2.connect')
    def test_verify_user_in_db_uncaught_error(self, mock_connect):
        mock_cur = setup_mock_cursor(mock_connect)
        mock_cur.execute.side_effect = Exception("Generic uncaught exception")
        expected_tuple: tuple[dict[str, str], Literal[500]] = \
            {'status': 'uncaught_error'}, 500

        random_cid = random_cid_generator()

        response = verify_user_in_db(random_cid)
        self.assertTupleEqual(
            tuple(expected_tuple), tuple(response))
        mock_cur.execute.assert_called_once_with("""UPDATE UserData
                SET verified = TRUE
                WHERE cid = %s""", (random_cid,))

    def test_verify_user_from_email_verification_success(self):
        random_cid = random_cid_generator()
        test_token = create_verification_token(random_cid)[0].get('Token')
        # with patch.object(bcrypt, 'gensalt') as mock_gensalt:
        mock_response = {'status': 'success'}, 200
        with patch('src.login_handler.verify_user_in_db', return_value=mock_response):
            # verify_result.return_value = {'status': 'success'}, 200
            verification_response = verify_user_from_email_verification(
                test_token)
            self.assertEqual(random_cid, verification_response[0].get('cid'))
