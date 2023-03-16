from unittest import mock
from src.user_handler import get_courses, get_course_group
import sys
from pathlib import Path
import unittest
from unittest.mock import MagicMock, patch
from psycopg2 import IntegrityError

sys.path.append(str(Path(__file__).absolute().parent.parent))


def setup_mock_cursor(mock_connect) -> MagicMock:
    mock_cursor = MagicMock()
    mock_conn = MagicMock()
    mock_connect.return_value = mock_conn
    mock_conn.cursor.return_value.__enter__.return_value = mock_cursor

    return mock_cursor


class TestUserHandler(unittest.TestCase):
    def setup(self):
        self.test_file_dir = Path(__file__).parent/"test_files_user_handler"

    @patch('psycopg2.connect')
    def test_get_user_courses(self, mock_connect):

        mock_cursor = setup_mock_cursor(mock_connect)
        mock_cursor.fetchall.return_value = [(1, 'Admin', 1, 'datx12', 2, 2023), (1, 'Student', 2, 'datx11', 4, 2023)]

        userId = 1
        result = get_courses(userId)
        mock_cursor.execute.assert_called_once_with("""SELECT * FROM User_course_info
                            WHERE userid = %s""", (userId,))
        self.assertEqual(
            result, [{'Role': 'Admin', 'courseID': 1, 'Course': 'datx12',
                      'Year': 2, 'StudyPeriod': 2023},
                     {'Role': 'Student', 'courseID': 2, 'Course': 'datx11',
                     'Year': 4, 'StudyPeriod': 2023}])

    @patch('psycopg2.connect')
    def test_get_user_group_from_courses(self, mock_connect):

        mock_cursor = setup_mock_cursor(mock_connect)
        mock_cursor.fetchone.return_value = (2, 1)

        userId = 1
        courseId = 6
        result = get_course_group(userId, courseId)

        mock_cursor.execute.assert_called_once_with("""SELECT groupid, groupnumber FROM
                                user_group_course_info
                                WHERE userid = %s and courseid = %s""",
                                                    (userId, courseId))
        self.assertEqual(result, {'groupid': 2, 'groupNumber': 1})
