from .connector import get_conn_string
import psycopg2
import datetime

# TODO: move course and assignment stuff from user_handler to here, implement create assignment


# TODO: not tested yet
def create_course(course_name: str, course_abbr: str, year: int,
                  teaching_period: int) -> tuple | int:
    """Cretes a course. Alos checks so the course data that is
    added is according to database requirements
    
    Returns: A dict with errors if they exists, otherwise the created course id"""
    response = {}
    if not (len(course_abbr) == 6):
        response['Course Abbreviation'] = 'Should be 6 characters'

    if not (year >= datetime.datetime.now().year()):
        response['Year'] = 'Cant be a year thats passed'

    if not (teaching_period <= 5 and teaching_period > 0):
        response['Teaching Period'] = 'Must be between 0-5'

    if (len(response) > 0):
        return response, 400

    else:
        id = __create_course(course_name, course_abbr, year, teaching_period)
    return id


# TODO: not tested yet
def add_groups_to_course(number_of_groups: int, course_id: int):
    """Creates a number of groups to the specified course, group number is set
    to the following integer that isnt already used for that course"""
    conn = psycopg2.connect(dsn=get_conn_string())

    try:
        with conn:
            with conn.cursor() as cur:
                query_one = """SELECT MAX(groupnumber) FROM Groups WHERE course = %s;"""
                cur.execute(query_one, [course_id])
                current_group: int = cur.fetchone()[0]
                if current_group is None:
                    current_group = 0
                
                for i in range(1, number_of_groups+1):
                    query_one = """Insert into Groups
                                (course, groupnumber)
                                values (%s,%s) """
                    cur.execute(query_one, [course_id, current_group + i])
            conn.close()

    except Exception as e:
        print(e)
        return None


def __create_course(course_name: str, course_abbr: str, year: int,
                    teaching_period: int) -> int:
    conn = psycopg2.connect(dsn=get_conn_string())

    try:
        with conn:
            with conn.cursor() as cur:
                query_one = """Insert into Courses
                                (coursename,course, teachingperiod, courseyear)
                                values (%s,%s,%s,%s) """
                cur.execute(query_one, [course_name,course_abbr, teaching_period, year])

                query_two = """select courseid from Courses
                                where  (course = %s AND
                                teachingperiod = %s AND courseyear = %s)"""
                cur.execute(query_two, [course_abbr, teaching_period, year])
                data = cur.fetchone()
            conn.close()
            return data[0]

    except Exception as e:
        print(e)
        return None


def create_assignment(course_id: int, description: str, assignment_nr: int,
                      end_date: str, file_names: tuple) -> dict | None:
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

        res = add_filenames(file_names, course_id, assignment_nr)

        return res

    except Exception as e:
        print(e)
        return {'status': 'Insert failed'}


def add_filenames(file_names: tuple(str), course_id: int,
                  assignment: int) -> None | dict:
    conn = psycopg2.connect(dsn=get_conn_string())

    try:
        with conn:
            with conn.cursor() as cur:
                for file in file_names:
                    query_one = """INSERT INTO FileNames (courseid, assignment, filename) VALUES
                                    (%s, %s, %s);"""
                    cur.execute(query_one, [course_id, assignment, file])

            conn.close()
        return
    except Exception as e:
        print(e)
        return {'status': 'Insert filenames failed'}


def check_file_extension(filename):
    """
    Check if a filename ends with ".py", ".txt" or ".pdf".
    """
    return filename.endswith((".py", ".txt", ".pdf"))


def check_date_format(date_string):
    """
    Check if a date string has the same structure as the Date type in PostgreSQL.
    """
    try:
        datetime.strptime(date_string, '%Y-%m-%d')
        return True
    except ValueError:
        return False
