import src.course_handler as course_handler
import sys
from pathlib import Path
import unittest
from unittest.mock import MagicMock, patch


sys.path.append(str(Path(__file__).absolute().parent.parent))


def setup_mock_cursor(mock_connect) -> MagicMock:
    mock_cursor = MagicMock()
    mock_conn = MagicMock()
    mock_connect.return_value = mock_conn
    mock_conn.cursor.return_value.__enter__.return_value = mock_cursor

    return mock_cursor


class TestCourseHandler(unittest.TestCase):
    def setup(self):
        self.test_file_dir = Path(__file__).parent/"test_files_course_handler"

    @patch('psycopg2.connect')
    def test_get_user_courses_info(self, mock_connect):
        with patch.object(course_handler, 'get_assignments') as mock_assignments:
            mock_assignments.return_value = []
            mock_cursor = setup_mock_cursor(mock_connect)
            mock_cursor.fetchall.return_value = [(1, 'Admin', 1, 'Whole course name', 'datx12', 2023, 3), (1, 'Student', 2, 'Whole course name', 'datx11', 2023, 2)]

            user_id = 1
            result = course_handler.get_courses_info(user_id)
            mock_cursor.execute.assert_called_once_with("""SELECT * FROM UserCourseInfo
                            WHERE userid = %s""", (user_id,))
            self.assertEqual(
                result, [{'Role': 'Admin', 'courseID': 1, 'CourseName': 'Whole course name', 'Course': 'datx12',
                          'Year': 2023, 'StudyPeriod': 3, 'Assignments': []},
                         {'Role': 'Student', 'courseID': 2, 'CourseName': 'Whole course name', 'Course': 'datx11',
                          'Year': 2023, 'StudyPeriod': 2, 'Assignments': []}, ])
