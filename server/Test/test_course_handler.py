import sys
from pathlib import Path
import unittest
from unittest.mock import MagicMock, patch

sys.path.append(str(Path(__file__).absolute().parent.parent))
import src.course_handler as course_handler  # noqa: E402


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
        with patch.object(
            course_handler, 'get_assignments'
        ) as mock_assignments:
            mock_assignments.return_value = []
            mock_cursor = setup_mock_cursor(mock_connect)
            mock_cursor.fetchall.return_value = [
                (1, 'Admin', 1, 'Whole course name', 'datx12', 3, 2023),
                (1, 'Student', 2, 'Whole course name', 'datx11', 2, 2023)
            ]

            user_id = 1
            result = course_handler.get_courses_info(user_id)
            mock_cursor.execute.assert_called_once_with(
                """SELECT * FROM UserCourseInfo
                            WHERE userid = %s""", (user_id,))
            self.assertEqual(
                result, [
                    {
                        'Role': 'Admin',
                        'courseID': 1,
                        'CourseName': 'Whole course name',
                        'Course': 'datx12',
                        'Year': 2023,
                        'StudyPeriod': 3,
                        'Assignments': []
                    },
                    {
                        'Role': 'Student',
                        'courseID': 2,
                        'CourseName': 'Whole course name',
                        'Course': 'datx11',
                        'Year': 2023,
                        'StudyPeriod': 2,
                        'Assignments': []
                    },
                ]
            )

    @patch('psycopg2.connect')
    def test_get_user_course_info(self, mock_connect):
        with patch.object(
            course_handler, 'get_assignments'
        ) as mock_assignments:
            mock_assignments.return_value = []
            mock_cursor = setup_mock_cursor(mock_connect)
            mock_cursor.fetchone.side_effect = [
                [1, 'Admin', 1, 'Whole course name', 'datx12', 2023, 3], ['name here']]
            user_id = 1
            course_id = 1
            result = course_handler.get_course_info(user_id, course_id)
            assert 2 == mock_cursor.execute.call_count
            self.assertEqual(
                result, {
                    'Role': 'Admin',
                    'courseID': 1,
                    'CourseName': 'Whole course name',
                    'Course': 'datx12',
                    'Year': 2023,
                    'StudyPeriod': 3,
                    'Assignments': [],
                    'Admin': 'name here'
                }
            )

    @patch('psycopg2.connect')
    def test_add_group_to_course(self, mock_connect):
        mock_cursor = setup_mock_cursor(mock_connect)
        mock_cursor.fetchone.side_effect = [[False], [3], None, None]
        course_id = 1
        user_id = 1
        course_handler.add_group_to_course(course_id, user_id)
        assert 4 == mock_cursor.execute.call_count

    @patch('psycopg2.connect')
    def test_get_assignments(self, mock_connect):
        mock_cursor = setup_mock_cursor(mock_connect)
        course_id = 1
        mock_cursor.fetchall.return_value = [
            (2, '2022-03-18', 'description', 'TestName',1,1)]
        res = course_handler.get_assignments(course_id)
        mock_cursor.execute.assert_called_once_with(
            "SELECT assignment, endDate, description, assignmentName,"
            "maxScore, passScore FROM Assignments WHERE courseId = %s",
            [course_id]
        )
        self.assertEqual(
            res, [{
                'AssignmentNr': 2,
                'DueDate': '2022-03-18',
                'Description': 'description',
                'Name': 'TestName',
                'MaxScore': 1,
                'PassScore': 1
            }])

    @patch('psycopg2.connect')
    def test_add_filenames(self, mock_connect):
        mock_cursor = setup_mock_cursor(mock_connect)
        course_id = 1
        file_names = ['file1.txt', 'file2.py']
        assignment = 2
        course_handler.add_filenames(file_names, course_id, assignment)
        assert 2 == mock_cursor.execute.call_count

    @patch('psycopg2.connect')
    def test_create_assignment(self, mock_connect):
        mock_cursor = setup_mock_cursor(mock_connect)
        course_id = 1
        desc = 'test desc'
        assignment_nr = 2
        end_date = '2024-01-11'
        file_names = ['file1.txt', 'file2.py']
        max_score = 5
        pass_score = 3
        mock_cursor.fetchone.return_value = [None]

        with patch.object(course_handler, 'add_filenames') as mock_files:
            course_handler.create_assignment(
                course_id, desc, assignment_nr, end_date, file_names,
                max_score, pass_score
            )
            assert 2 == mock_cursor.execute.call_count
        mock_files.assert_called_once_with(
            file_names, course_id, 1)

    @patch('psycopg2.connect')
    def test_change_desc(self, mock_connect):
        mock_cursor = setup_mock_cursor(mock_connect)
        new_desc = "New desc"
        course = 1
        assignment = 1
        res = course_handler.change_description(new_desc, course, assignment)
        assert res is None

        mock_cursor.execute.side_effect = Exception("Database error")
        res = course_handler.change_description(new_desc, course, assignment)
        assert isinstance(res, dict)
