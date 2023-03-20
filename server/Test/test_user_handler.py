
import src.user_handler as user_handler
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


class TestUserHandler(unittest.TestCase):
    def setup(self):
        self.test_file_dir = Path(__file__).parent/"test_files_user_handler"

    @patch('psycopg2.connect')
    def test_get_user_courses_info(self, mock_connect):
        with patch.object(user_handler, 'get_assignments') as mock_assignments:
            mock_assignments.return_value = []
            mock_cursor = setup_mock_cursor(mock_connect)
            mock_cursor.fetchall.return_value = [(1, 'Admin', 1, 'datx12', 2, 2023), (1, 'Student', 2, 'datx11', 4, 2023)]

            user_id = 1
            result = user_handler.get_courses_info(user_id)
            mock_cursor.execute.assert_called_once_with("""SELECT * FROM User_course_info
                            WHERE userid = %s""", (user_id,))
            self.assertEqual(
                result, [{'Role': 'Admin', 'courseID': 1, 'Course': 'datx12',
                      'Year': 2, 'StudyPeriod': 2023, 'Assignments': []},
                     {'Role': 'Student', 'courseID': 2, 'Course': 'datx11',
                     'Year': 4, 'StudyPeriod': 2023, 'Assignments': []}, ])

    @patch('psycopg2.connect')
    def test_get_group(self, mock_connect):
        with patch.object(user_handler, '__get_group_members') as mock_groups:
            mock_cursor = setup_mock_cursor(mock_connect)
            mock_cursor.fetchone.return_value = (2, 1)
            mock_groups.return_value = ['alebru']     
            user_id = 1
            course_id = 6
            result = user_handler.get_group(user_id, course_id)

            mock_cursor.execute.assert_called_once_with("""SELECT groupid, groupnumber FROM
                                user_group_course_info
                                WHERE userid = %s and courseid = %s""",
                                                        (user_id, course_id))
            self.assertEqual(result, {'groupId': 2, 'groupNumber': 1, 'groupMembers': ['alebru']})

    @patch('psycopg2.connect')
    def test_add_user_to_course(self, mock_connect):
        mock_cursor = setup_mock_cursor(mock_connect)
        user_id = 1
        course_id = 6
        user_handler.add_user_to_course(user_id, course_id, user_handler.Role.Student)

        mock_cursor.execute.assert_called_once_with("""INSERT into userincourse values
                                (%s, %s, %s)""", [user_id, course_id, user_handler.Role.Student.name])

    @patch('psycopg2.connect')
    def test_remove_user_from_group(self, mock_connect):
        user_id = 1
        group_id = 1
        mock_cursor = setup_mock_cursor(mock_connect)
        user_handler.remove_user_from_group(user_id, group_id)

        mock_cursor.execute.assert_called_once_with("""DELETE from useringroup
                                WHERE userid = %s AND groupid = %s """,
                                                    [user_id, group_id])

    @patch('src.user_handler.get_courses_info')
    def test_is_admin_on_course(self, mock_user_courses):
        user_id = 1
        course_id = 1
        mock_user_courses.return_value = [{'Role': 'Admin', 'courseID': 1,
                                           'Course': 'datx12',
                                           'Year': 2, 'StudyPeriod': 2023},
                                          {'Role': 'Student', 'courseID': 2,
                                           'Course': 'datx11',
                                           'Year': 4, 'StudyPeriod': 2023}]
        res: bool = user_handler.is_admin_on_course(user_id, course_id)
        mock_user_courses.assert_called_once_with(user_id)
        self.assertTrue(res)

    @patch('src.user_handler.get_courses_info')
    def test_is_not_admin_on_course(self, mock_user_courses):
        user_id = 1
        course_id = 1
        mock_user_courses.return_value = [{'Role': 'Teacher', 'courseID': 1,
                                           'Course': 'datx12',
                                           'Year': 2, 'StudyPeriod': 2023},
                                          {'Role': 'Student', 'courseID': 2,
                                           'Course': 'datx11',
                                           'Year': 4, 'StudyPeriod': 2023}]
        res: bool = user_handler.is_admin_on_course(user_id, course_id)
        mock_user_courses.assert_called_once_with(user_id)
        self.assertFalse(res)

    @patch('src.user_handler.get_courses_info')
    def test_is_Teacher_on_course(self, mock_user_courses):
        user_id = 1
        course_id = 1
        mock_user_courses.return_value = [{'Role': 'Teacher', 'courseID': 1,
                                           'Course': 'datx12',
                                           'Year': 2, 'StudyPeriod': 2023},
                                          {'Role': 'Student', 'courseID': 2,
                                           'Course': 'datx11',
                                           'Year': 4, 'StudyPeriod': 2023}]
        res: bool = user_handler.is_teacher_on_course(user_id, course_id)
        mock_user_courses.assert_called_once_with(user_id)
        self.assertTrue(res)

    @patch('src.user_handler.get_courses_info')
    def test_is_not_teacher_on_course(self, mock_user_courses):
        user_id = 1
        course_id = 1
        mock_user_courses.return_value = [{'Role': 'Student', 'courseID': 1,
                                           'Course': 'datx12',
                                           'Year': 2, 'StudyPeriod': 2023},
                                          {'Role': 'Student', 'courseID': 2,
                                           'Course': 'datx11',
                                           'Year': 4, 'StudyPeriod': 2023}]
        res: bool = user_handler.is_teacher_on_course(user_id, course_id)
        mock_user_courses.assert_called_once_with(user_id)
        self.assertFalse(res)
