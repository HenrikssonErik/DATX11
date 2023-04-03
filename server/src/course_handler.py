from .connector import get_conn_string
import psycopg2
import datetime


def create_course(course_name: str, course_abbr: str, year: int,
                  teaching_period: int) -> tuple | int:
    """Cretes a course. Also checks so the course data that is
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
        id = __create_course(course_name, course_abbr, year, teaching_period)
    return id


def get_courses_info(user_id: int) -> list[dict[str, any]]:
    """Returns an array with information on Courses associated to the userId"""
    conn = psycopg2.connect(dsn=get_conn_string())

    try:
        with conn:
            with conn.cursor() as cur:
                query_data = """SELECT * FROM UserCourseInfo
                            WHERE userid = %s"""
                cur.execute(query_data, (user_id,))
                data = cur.fetchall()
        conn.close()
        if not data:
            return []
        orderedData: list[dict[str, any]] = []
        for info in data:
            orderedData.append({"Role": info[1], "courseID": info[2],
                                "CourseName": info[3],
                                "Course": info[4], "Year": info[5],
                                "StudyPeriod": info[6],
                                'Assignments': get_assignments(info[2])})
        return orderedData

    except Exception as e:
        print(e)
        return [{'status': "No Courses Found"}]


def get_course_info(user_id: int, course_id: int):
    """Returns a dict with information on the specified course associated to
    the user_id, course_id"""
    conn = psycopg2.connect(dsn=get_conn_string())

    try:
        with conn:
            with conn.cursor() as cur:
                query_data = """SELECT * FROM UserCourseInfo
                            WHERE userid = %s AND courseid=%s"""
                cur.execute(query_data, [user_id, course_id])
                data = cur.fetchone()
        conn.close()
        if not data:
            raise Exception("No Courses Found")

        orderedData: dict[str, any] = {}
        orderedData["Role"] = data[1]
        orderedData["courseID"] = data[2]
        orderedData["CourseName"] = data[3]
        orderedData["Course"] = data[4]
        orderedData["Year"] = data[5]
        orderedData["StudyPeriod"] = data[6]
        orderedData['Assignments'] = get_assignments(data[2])
        return orderedData

    except Exception as e:
        print(e)
        return [{'status': "No Courses Found"}]


def add_groups_to_course(number_of_groups: int, course_id: int) -> None:
    """Creates a number of groups to the specified course, group number is set
    to the following integer that isnt already used for that course"""
    conn = psycopg2.connect(dsn=get_conn_string())

    try:
        with conn:
            with conn.cursor() as cur:
                query_one = """SELECT MAX(groupnumber) FROM Groups WHERE
                course = %s"""
                cur.execute(query_one, [course_id])
                current_group: int = cur.fetchone()[0]
                if current_group is None:
                    current_group = 0

                for i in range(1, number_of_groups+1):
                    query_one = """Insert into Groups
                    (course, groupnumber) values (%s,%s) """
                    cur.execute(query_one, [course_id, current_group + i])
        conn.close()

    except Exception as e:
        print(e)
        return None


def __create_course(course_name: str, course_abbr: str, year: int,
                    teaching_period: int) -> int | tuple:
    """Internal method to create a course, used by create_course method after verification of data
    Returnsthe new course ID"""
    conn = psycopg2.connect(dsn=get_conn_string())

    try:
        with conn:
            with conn.cursor() as cur:
                query_one = """Insert into Courses
                                (coursename,course, teachingperiod, courseyear)
                                values (%s,%s,%s,%s) """
                cur.execute(query_one, [course_name, course_abbr,
                                        teaching_period, year])

                query_two = """select courseid from Courses
                                where  (course = %s AND
                                teachingperiod = %s AND courseyear = %s)"""
                cur.execute(query_two, [course_abbr, teaching_period, year])
                data = cur.fetchone()
        conn.close()
        return data[0]

    except Exception as e:
        print(e)
        return {'status': "course_exists"}, 400


def create_assignment(course_id: int, description: str, assignment_nr: int,
                      end_date: str, file_names: list) -> dict:
    """Creates an assignment for a course, assignment number will not be incremented automatically,
    thus must be provided by the creator"""
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
                query_one = """INSERT INTO Assignments VALUES
                                (%s, %s, %s, %s);"""
                cur.execute(query_one, [course_id, assignment_nr, description,
                                        end_date])
        conn.close()

        add_filenames(file_names, course_id, assignment_nr)

        return res

    except Exception as e:
        print(e)
        return {'status': 'Insert failed'}


def get_assignments(course_id: int) -> tuple:
    """Returns a list of all assignments connected to a course, with their description and end date"""
    conn = psycopg2.connect(dsn=get_conn_string())

    try:
        with conn:
            with conn.cursor() as cur:
                query_data = """SELECT assignment, enddate, Description FROM
                                assignments WHERE courseid = %s"""
                cur.execute(query_data, [course_id])
                # data = [row[0] for row in cur.fetchall()]
                data = cur.fetchall()
                assignments: list[dict[str:any]] = []
                for assignmentRow in data:
                    assignments.append({'AssignmentNr': assignmentRow[0],
                                        'DueDate': assignmentRow[1],
                                        'Description': assignmentRow[2]})
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
                query_data = """UPDATE assignments set description = %s
                                WHERE courseid = %s and assignment = %s"""
                cur.execute(query_data, [new_desc, course_id, assignment])
                
        conn.close()
        return None

    except Exception as e:
        print(e)
        return {'status': "No Courses Found"}


# TODO: not done or tested, returns statements must be fixed
def set_teacher_feedback(group_id: int, feedback: str, grade: bool, 
                         passed: bool, course: int, assignment: int):
    """Submission is set to 0 since a primary cannot be null. 
    It will increment by default anyway."""
    conn = psycopg2.connect(dsn=get_conn_string())
    try:
        with conn:
            with conn.cursor() as cur:
                query_one = """INSERT INTO AssignmentFeedback (groupId,
                courseId, assignment, submission, teacherGrade, teacherFeedback, testPassed)
                VALUES (%s, %s, %s, 0, %s, %s, %s);"""
                cur.execute(query_one, [group_id, course, assignment, 0, grade,
                                        feedback, passed])
        conn.close()
        return
    except Exception as e:
        print(e)
        return {'status': 'Could Not update the feedback'}


# Not tested
def change_end_date(course: int, assignment: int,
                    new_date: str) -> dict | None:
    """Changes the end-date of the specified assignment
    Returns a dict if error occurs, otherwise None"""
    if (check_date_format(new_date)):
        conn = psycopg2.connect(dsn=get_conn_string())

        try:
            with conn:
                with conn.cursor() as cur:
                    query_one = """UPDATE assignments SET enddate = %s
                    WHERE courseid = %s AND assignment = %s;"""
                    cur.execute(query_one, [new_date, course, assignment])
            conn.close()
            return
        except Exception as e:
            print(e)
            return {'status': 'Something went wrong'}
    else:
        return {'status': 'End date has the wrong format, must be YYYY-MM-DD'}


def add_filenames(file_names: list, course_id: int,
                  assignment: int) -> None:
    """ Adds thelist of filenames to allowed filenames for the specified
    assignment"""
    conn = psycopg2.connect(dsn=get_conn_string())

    try:
        with conn:
            with conn.cursor() as cur:
                for file in file_names:
                    query_one = """INSERT INTO FileNames (courseid, assignment,
                                    filename) VALUES
                                    (%s, %s, %s);"""
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
