from .connector import get_conn_string
import psycopg2
import datetime
from . import user_handler


def create_course(course_name: str, course_abbr: str, year: int,
                  teaching_period: int) -> tuple | int:
    """Creates a course. Also checks so the course data that is
    added is according to database requirements

    Returns: A dict with errors if they exists,
            otherwise the created course id"""
    response = {}
    if not (len(course_abbr) == 6):
        response['Course Abbreviation'] = 'Should be 6 characters'

    if not (year >= datetime.datetime.now().year):
        response['Year'] = 'Cant be a year thats passed'

    if not (teaching_period <= 5 and teaching_period > 0):
        response['Teaching Period'] = 'Must be between 0-5'

    if (len(response) > 0):
        return response, 400

    else:
        id = _create_course(course_name, course_abbr, year, teaching_period)
    return id


def get_courses_info(user_id: int) -> list[dict[str, str | int]]:
    """Returns an array with information on Courses associated to the userId"""
    conn = psycopg2.connect(dsn=get_conn_string())

    try:
        with conn:
            with conn.cursor() as cur:
                query_data = """SELECT * FROM UserCourseInfo
                            WHERE userId = %s"""
                cur.execute(query_data, (user_id,))
                data = cur.fetchall()
        conn.close()
        if not data:
            return []
        ordered_data: list[dict[str, str | int]] = []
        for info in data:
            ordered_data.append({"Role": info[1], "courseID": info[2],
                                "CourseName": info[3],
                                 "Course": info[4], "Year": info[6],
                                 "StudyPeriod": info[5],
                                 'Assignments': get_assignments(info[2])})
        return ordered_data

    except Exception as e:
        print(e)
        return [{'status': "No Courses Found"}]


def get_course_info(user_id: int, course_id: int) -> dict[str, str | int]:
    """Returns a dict with information on the specified course associated to
    the user_id, course_id"""
    conn = psycopg2.connect(dsn=get_conn_string())

    try:
        with conn:
            with conn.cursor() as cur:
                query_data = """SELECT * FROM UserCourseInfo
                            WHERE userId = %s AND courseId=%s"""
                cur.execute(query_data, [user_id, course_id])
                data = cur.fetchone()
                query_two = """SELECT ud.fullName FROM UserData ud JOIN
                UserInCourse uc ON uc.userId = ud.userId WHERE uc.courseId = %s
                AND uc.userRole = 'Admin';"""
                cur.execute(query_two, [course_id])
                admin = cur.fetchone()
        conn.close()
        if not data:
            raise Exception("No Courses Found")

        ordered_data: dict[str, str | int] = {}
        ordered_data["Role"] = data[1]
        ordered_data["courseID"] = data[2]
        ordered_data["CourseName"] = data[3]
        ordered_data["Course"] = data[4]
        ordered_data["Year"] = data[5]
        ordered_data["StudyPeriod"] = data[6]
        ordered_data['Assignments'] = get_assignments(data[2])
        if (admin):
            ordered_data['Admin'] = admin[0]
        return ordered_data

    except Exception as e:
        print(e)
        return {'status': "No Courses Found"}


def get_progress(user_id: int) -> list[dict]:
    """Retrieves the results of the latest submisison for the user on
    all courses"""
    conn = psycopg2.connect(dsn=get_conn_string())

    try:
        with conn:
            with conn.cursor() as cur:
                query = """SELECT tf.courseId, COUNT(*) AS Completed FROM
                UserGroupCourseInfo ugci JOIN (SELECT courseId, assignmentId,
                globalGroupId, MAX(submissionNumber) AS maxSubmissionNumber
                FROM TotalFeedback GROUP BY courseId, assignmentId,
                globalGroupId) maxSub ON
                ugci.globalGroupId = maxSub.globalGroupId AND
                ugci.courseId = maxSub.courseId JOIN TotalFeedback tf ON
                ugci.globalGroupId = tf.globalGroupId AND
                ugci.courseId = tf.courseId AND
                tf.assignmentId = maxSub.assignmentId AND
                tf.submissionNumber = maxSub.maxSubmissionNumber WHERE
                ugci.userId = %s AND tf.teacherGrade = TRUE
                GROUP BY tf.courseId;"""
                cur.execute(query, [user_id])
                data = cur.fetchall()
        conn.close()
        if not (data):
            return []
        else:
            courses = [{'Course': row[0], 'Completed': row[1]} for row in data]
            return courses

    except Exception as e:
        print(e)
        raise Exception("Could not get status") from e


def add_group_to_course(course_id: int, user_id: int):
    """Creates a  group to the specified course and adds the user to it,
    group number is set to the following integer that isnt already used
    for that course"""
    conn = psycopg2.connect(dsn=get_conn_string())

    try:
        with conn:
            with conn.cursor() as cur:
                query = """SELECT EXISTS(SELECT 1 FROM
                        UserGroupCourseInfo WHERE courseId=%s AND userId=%s) AS
                        exists_row;"""
                cur.execute(query, [course_id, user_id])
                in_group = cur.fetchone()[0]
                if not (in_group):
                    query_one = """SELECT MAX(groupNumberInCourse) FROM Groups WHERE
                    courseId = %s"""
                    cur.execute(query_one, [course_id])
                    current_group: int = cur.fetchone()[0]
                    if current_group is None:
                        current_group = 0

                    query_two = """INSERT INTO Groups
                        (courseId, groupNumberInCourse) VALUES (%s,%s) """
                    cur.execute(query_two, [course_id, current_group + 1])
                    query_three = """INSERT INTO UserInGroup (userId, globalGroupId)
                    SELECT %s, gd.globalGroupId FROM GroupDetails gd WHERE
                    gd.groupNumberInCourse = %s AND gd.courseId = %s;"""
                    cur.execute(query_three, [user_id, current_group+1,
                                              course_id])
                else:
                    raise Exception("Already in group")
        conn.close()

    except Exception as e:
        print(e)
        raise Exception("Could not create group") from e


def _create_course(course_name: str, course_abbr: str, year: int,
                   teaching_period: int) -> int | tuple[dict[str, str], int]:
    """Internal method to create a course, used by create_course method after
    verification of data. Returns the new course ID"""
    conn = psycopg2.connect(dsn=get_conn_string())

    try:
        with conn:
            with conn.cursor() as cur:
                query_one = """Insert into Courses
                                (courseName, coursecode, teachingPeriod,
                                courseYear) values (%s,%s,%s,%s) """
                cur.execute(query_one, [course_name, course_abbr,
                                        teaching_period, year])

                query_two = """select courseid from Courses
                                where  (coursecode = %s AND
                                teachingperiod = %s AND courseyear = %s)"""
                cur.execute(query_two, [course_abbr, teaching_period, year])
                data = cur.fetchone()
        conn.close()
        return data[0]

    except Exception as e:
        print(e)
        return {'status': "course_exists"}, 400


def create_assignment(course_id: int, description: str, assignment_name: int,
                      end_date: str, file_names: list, max_score: int,
                      pass_score: int) -> dict:
    """Creates an assignment for a course, assignment number will not be
    incremented automatically, thus must be provided by the creator"""
    res: dict = {}
    for name in file_names:
        if not (check_file_extension(name)):
            res[name] = 'Is of incorrect type, must be .py, .pdf or .txt'

    if not (check_date_format(end_date)):
        res['Date'] = 'End date has the wrong format, must be YYYY-MM-DD'

    if not (len(res) == 0):
        return {'status': res}

    conn = psycopg2.connect(dsn=get_conn_string())

    try:
        with conn:
            with conn.cursor() as cur:
                query_one = """SELECT MAX(assignmentid) as max_assignment FROM
                Assignments WHERE courseid = %s;"""
                cur.execute(query_one, [course_id])
                data = cur.fetchone()
                print(data)
                if data[0] is None:
                    assignment_nr = 1
                else:
                    # since the "select max" call is done before insert we
                    # need to increment by 1
                    assignment_nr = data[0] + 1
                query_two = """INSERT INTO Assignments (courseId, assignmentId,
                endDate, description, assignmentName, maxScore, passScore) VALUES
                    (%s, 0, %s, %s, %s, %s, %s);"""
                cur.execute(
                    query_two,
                    [
                        course_id,
                        end_date,
                        description,
                        assignment_name,
                        max_score,
                        pass_score
                    ]
                )
        conn.close()
        add_filenames(file_names, course_id, assignment_nr)
        return res

    except Exception as e:
        print(e)
        raise Exception("Could not create assignment") from e


def get_assignments(course_id: int) -> list[dict] | dict[str, str]:
    """Returns a list of all assignments connected to a course, with their
    description and end date"""
    conn = psycopg2.connect(dsn=get_conn_string())

    try:
        with conn:
            with conn.cursor() as cur:
                query_data = "SELECT Assignmentid, endDate, description, "\
                    "assignmentName, maxScore, passScore FROM Assignments"\
                    " WHERE courseId = %s"
                cur.execute(query_data, [course_id])
                # data = [row[0] for row in cur.fetchall()]
                data = cur.fetchall()
                assignments: list[dict[str, str | int]] = []
                for assignment_row in data:
                    assignments.append({'AssignmentNr': assignment_row[0],
                                        'DueDate': assignment_row[1],
                                        'Description': assignment_row[2],
                                        'Name': assignment_row[3],
                                        'MaxScore': assignment_row[4],
                                        'PassScore': assignment_row[5]})
        conn.close()
        if not data:
            return []
        return assignments

    except Exception as e:
        print(e)
        return {'status': "No Courses Found"}


def change_description(new_desc: str, course_id: int,
                       assignment: int) -> dict | None:
    """ Changes the description for the a assignment"""
    conn = psycopg2.connect(dsn=get_conn_string())

    try:
        with conn:
            with conn.cursor() as cur:
                query_data = """UPDATE Assignments SET description = %s
                                WHERE courseId = %s AND assignmentId = %s"""
                cur.execute(query_data, [new_desc, course_id, assignment])

        conn.close()
        return None

    except Exception as e:
        print(e)
        return {'status': "No Courses Found"}


def change_assignment_name(new_name: str, course_id: int,
                           assignment: int):
    """ Changes the description for the a assignment"""
    conn = psycopg2.connect(dsn=get_conn_string())

    try:
        with conn:
            with conn.cursor() as cur:
                query_data = """UPDATE Assignments set assignmentName = %s
                                WHERE courseId = %s and assignmentId = %s"""
                cur.execute(query_data, [new_name, course_id, assignment])

        conn.close()
        return

    except Exception as e:
        print(e)
        raise Exception("could not change name") from e


def change_course_name(new_name: str, course: int):
    """ Changes the name for the course"""
    conn = psycopg2.connect(dsn=get_conn_string())

    try:
        with conn:
            with conn.cursor() as cur:
                query_data = """UPDATE courses set coursename = %s
                                WHERE courseid = %s"""
                cur.execute(query_data, [new_name, course])
        conn.close()

    except Exception as e:
        print(e)
        raise Exception("Could not change name") from e


def set_teacher_feedback(group_id: int, feedback: str, grade: bool,
                         course: int, assignment: int, submission: int,
                         teacher: int, score: int):
    """Submission is set to 0 since a primary cannot be null.
    It will increment by default anyway."""
    conn = psycopg2.connect(dsn=get_conn_string())
    try:
        with conn:
            with conn.cursor() as cur:
                query_one = """INSERT INTO TeacherFeedback 
                                (teacherFeedback, teacherGrade, teacherFeedbackDate, 
                                assignmentScore, courseId, userId, globalGroupId, 
                                submissionNumber, assignmentId)
                            VALUES 
                                (%s, %s, 
                                (CURRENT_TIMESTAMP AT TIME ZONE 'Europe/Stockholm'), 
                                %s, %s, %s, %s, %s, %s)
                            ON CONFLICT (courseId, globalgroupid, assignmentid, submissionnumber) DO 
                            UPDATE SET
                                teacherFeedback = %s, teacherGrade = %s,
                                teacherFeedbackDate = (CURRENT_TIMESTAMP AT TIME ZONE
                                'Europe/Stockholm'), assignmentScore = %s, courseId = %s,
                                userId = %s WHERE TeacherFeedback.globalGroupId = %s AND
                                TeacherFeedback.submissionNumber = %s AND TeacherFeedback.assignmentId = %s;"""
                cur.execute(query_one, [feedback, grade, score, course,
                                        teacher, group_id, submission,
                                        assignment, feedback, grade, score, course,
                                        teacher, group_id, submission,
                                        assignment])
        conn.close()
        return
    except Exception as e:
        print(e)
        raise Exception("Could not update feedback") from e


# Not tested
def change_end_date(course: int, assignment: int,
                    new_date: str) -> dict[str, str] | None:
    """Changes the end-date of the specified assignment
    Returns a dict if error occurs, otherwise None"""
    if (check_date_format(new_date)):
        conn = psycopg2.connect(dsn=get_conn_string())

        try:
            with conn:
                with conn.cursor() as cur:
                    query_one = """UPDATE Assignments SET endDate = %s
                    WHERE courseId = %s AND assignmentId = %s;"""
                    cur.execute(query_one, [new_date, course, assignment])
            conn.close()
            return
        except Exception as e:
            print(e)
            raise Exception("Could not change end date") from e
    else:
        return {'status': 'End date has the wrong format, must be YYYY-MM-DD'}


def add_filenames(file_names: list, course_id: int,
                  assignment: int):
    """ Adds thelist of filenames to allowed filenames for the specified
    assignment"""
    conn = psycopg2.connect(dsn=get_conn_string())

    try:
        with conn:
            with conn.cursor() as cur:
                for file in file_names:
                    query_one = """INSERT INTO RequiredFileNames 
                                (courseId, assignmentId, assignmentFileName) 
                                VALUES (%s, %s, %s);"""
                    cur.execute(query_one, [course_id, assignment, file])

        conn.close()
        return
    except Exception as e:
        print(e)


def check_file_extension(filename) -> bool:
    """
    Check if a filename ends with ".py", ".txt" or ".pdf".
    """
    return filename.endswith((".py", ".txt", ".pdf"))


def check_date_format(date_string) -> bool:
    """
    Check if a date string has the same structure as the
    Date type in PostgreSQL.
    """
    try:
        datetime.datetime.strptime(date_string, '%Y-%m-%d')
        return True
    except ValueError:
        return False


def get_assignment_feedback(course: int, assignment: int,
                            group: int) -> list[dict[str, str | int | None]]:
    conn = psycopg2.connect(dsn=get_conn_string())

    try:
        with conn:
            with conn.cursor() as cur:
                query_data = """SELECT 
                                    submissionNumber, 
                                    testPassed,
                                    automaticFeedback, 
                                    teacherFeedback, 
                                    teacherGrade, 
                                    userId,
                                    teacherfeedbackdate 
                                FROM TotalFeedback 
                                WHERE 
                                    courseId = %s AND
                                    globalGroupId = %s AND 
                                    assignmentId = %s"""
                cur.execute(query_data, (course, group, assignment))
                data = cur.fetchall()

        conn.close()
        if not data:
            return []
        return _format_assignment_feedback(data)

    except Exception as e:
        print(e)
        raise Exception("Could not retrieve feedback") from e


def _format_assignment_feedback(
        db_output: list[tuple]
) -> list[dict[str, str | int | None]]:
    assignments: list[dict[str, str | int | None]] = []
    for submission in db_output:
        testfeedback = "" if (x := submission[2]) is None else x

        teacherfeedback = "" if (x := submission[3]) is None else x

        grade = None if (x := submission[4]) is None else x

        if (x := submission[5]) is None:
            teacher = ""
        else:
            teacher = user_handler.get_fullname(x)

        assignments.append({'Submission': submission[0],
                            'testpass': submission[1],
                            'testfeedback': testfeedback,
                            'teacherfeedback': teacherfeedback,
                            'Grade': grade,
                            'GradedBy': teacher,
                            'Date': submission[6]})
    return assignments


def get_course_groups(course: int) -> list[dict[str, str | int]]:
    conn = psycopg2.connect(dsn=get_conn_string())

    try:
        with conn:
            with conn.cursor() as cur:
                query_data = """SELECT groupNumberInCourse, globalGroupId,
                array_agg(fullName) FROM GroupDetails WHERE courseid = %s GROUP
                BY globalGroupId, groupNumberInCourse"""
                cur.execute(query_data, [course])
                data = cur.fetchall()
                group_list = []
                if not data:
                    return []
                for row in data:
                    group_dict = {
                        "groupNumber": row[0],
                        "groupId": row[1],
                        "groupMembers": row[2]}
                    group_list.append(group_dict)
        conn.close()
        return group_list

    except Exception as e:
        print(e)
        raise Exception("Error when getting course groups") from e


def get_course_group(course: int, group_id: int) -> dict[str, str | int]:
    conn = psycopg2.connect(dsn=get_conn_string())

    try:
        with conn:
            with conn.cursor() as cur:
                query_data = """SELECT groupNumberInCourse,
                array_agg(fullName) FROM GroupDetails WHERE courseId = %s AND
                globalGroupId = %s GROUP BY globalGroupId, groupNumberInCourse"""
                cur.execute(query_data, [course, group_id])
                data = cur.fetchone()
                if data is None:
                    return {}
                group_dict = {
                    "groupNumber": data[0],
                    "users": data[1]}
        conn.close()
        return group_dict

    except Exception as e:
        print(e)
        raise Exception("Error when getting course groups") from e


def get_assignment_overview(course: int) -> list[dict]:
    """Returns a list with test status and grade for all the latest
    submissions for a assignment"""
    conn = psycopg2.connect(dsn=get_conn_string())

    try:
        with conn:
            with conn.cursor() as cur:
                query_one = """ SELECT assignmentId FROM Assignments WHERE
                courseId = %s"""
                cur.execute(query_one, [course])

                assignments = cur.fetchall()

                query_data = """SELECT DISTINCT ON (globalgroupId) globalgroupId, testPassed,
                teacherGrade, submissionNumber, assignmentScore,  teacherFeedback, userId,
                teacherfeedbackdate, createdDate FROM totalfeedback WHERE
                courseId = %s AND assignmentId = %s ORDER BY globalGroupId,
                submissionNumber DESC;"""
                return_list = []
                for assignment in assignments:
                    overview_list = []
                    cur.execute(query_data, [course, assignment[0]])
                    data = cur.fetchall()
                    if data:
                        for row in data:
                            teacher = "" if (
                                x := row[6]) is None else user_handler.get_fullname(x)
                            group = get_group_number(course, row[0])
                            group_dict = {
                                "groupid": row[0],
                                "testpass": row[1],
                                "grade": row[2],
                                'Submission': row[3],
                                "Score": row[4],
                                "Feedback": row[5],
                                "GradedBy": teacher,
                                'lastEdited': row[7],
                                'dateSubmitted': row[8],
                                'GroupNumber': group}
                            overview_list.append(group_dict)
                    return_list.append({"Assignment": assignment[0],
                                        "Submissions": overview_list})
        conn.close()
        return return_list

    except Exception as e:
        print(e)
        raise Exception("Error when getting assignment overview") from e


def get_group_number(course_id: int, group_id) -> int:
    """Returns  group number associated with the group_id
        in the specified course"""
    conn = psycopg2.connect(dsn=get_conn_string())
    print('course and group', course_id, group_id)
    try:
        with conn:
            with conn.cursor() as cur:
                query_data = """SELECT groupNumberInCourse FROM Groups WHERE
                courseId = %s and globalGroupId = %s"""
                cur.execute(query_data, (course_id, group_id))
                data = cur.fetchone()
        conn.close()

        if data is None:
            raise Exception("No group found")

        return data[0]
    except Exception as e:
        print(e)
        raise Exception("Could not find any group") from e


def passed_deadline(course: int, assignment: int) -> bool:
    conn = psycopg2.connect(dsn=get_conn_string())

    try:
        with conn:
            with conn.cursor() as cur:
                query_one = """SELECT endDate FROM Assignments
                    WHERE courseId = %s AND assignmentId = %s;"""
                cur.execute(query_one, [course, assignment])
                date = cur.fetchone()[0]
        conn.close()

        return date < datetime.date.today()

    except Exception as e:
        print(e)
        raise Exception("Could not get the deadline from database") from e
