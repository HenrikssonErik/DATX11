from .connector import get_conn_string
import psycopg2
import datetime

# TODO: move course and assignment stuff from user_handler to here

# TODO: not tested yet
def create_course(course_abbr: str, year: int,
                  teaching_period: int) -> tuple | int:
    """Cretes a course. Alos checks so the course data that is
    added is according to database requirements
    
    Returns: A dict with errors if they exists, otherwise the created course id"""
    response = {}
    if not (len(course_abbr) == 6):
        response['Course Abbreviation'] = 'Should be 6 characters'

    if not (year >= datetime.datetime.now().year() ):
        response['Year'] = 'Cant be a year thats passed'

    if not (teaching_period <= 5 and teaching_period > 0):
        response['Teaching Period'] = 'Must be between 0-5'

    if (len(response) > 0):
        return response, 400

    else:
        id = __create_course(course_abbr, year, teaching_period)
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


def __create_course(course_abbr: str, year: int, teaching_period: int) -> int:
    conn = psycopg2.connect(dsn=get_conn_string())

    try:
        with conn:
            with conn.cursor() as cur:
                query_one = """Insert into Courses
                                (course, teachingperiod, courseyear)
                                values (%s,%s,%s) """
                cur.execute(query_one, [course_abbr, teaching_period, year])

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
