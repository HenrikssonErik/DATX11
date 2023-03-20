from .connector import get_conn_string
import psycopg2
from enum import Enum


class Role(Enum):
    Admin = 'Admin'
    Teacher = 'Teacher'
    Student = 'Student'


def get_courses_info(user_id: int) -> list[dict[str, any]]:
    """Returns an array with information on Courses associated to the userId"""
    conn = psycopg2.connect(dsn=get_conn_string())

    try:
        with conn:
            with conn.cursor() as cur:
                query_data = """SELECT * FROM User_course_info
                            WHERE userid = %s"""
                cur.execute(query_data, (user_id,))
                data = cur.fetchall()
        conn.close()
        if not data:
            raise Exception("No courses for this user")
        orderedData: list[dict[str, any]] = []
        for info in data:
            orderedData.append({"Role": info[1], "courseID": info[2],
                                "Course": info[3], "Year": info[4],
                                "StudyPeriod": info[5]})
        return orderedData

    except Exception as e:
        print(e)
        return {'status': "No Courses Found"}


def get_group(user_id: int, course_id: int) -> dict[str, str]:
    """Returns group ID and group number associated with the users group
        in the specified course"""
    conn = psycopg2.connect(dsn=get_conn_string())

    try:
        with conn:
            with conn.cursor() as cur:
                query_data = """SELECT groupid, groupnumber FROM
                                user_group_course_info
                                WHERE userid = %s and courseid = %s"""
                cur.execute(query_data, (user_id, course_id))
                data = cur.fetchone()
        conn.close()

        if not data:
            raise Exception("No groups for this user")

        orderedData: dict = {}
        orderedData["groupId"] = data[0]
        orderedData["groupNumber"] = data[1]
        return orderedData

    except Exception as e:
        print(e)
        return {'status': "No Groups Found"}


def add_user_to_group(user_id: int, group_id: int) -> None:
    # check user on course and group on the course
    user_courses = get_courses_info(user_id)
    conn = psycopg2.connect(dsn=get_conn_string())

    course_id = __get_course_id_from_group(group_id)

    # add to group
    try:
        for course in user_courses:
            if course['courseID'] == course_id and \
               course['Role'] == Role.Student.name:
                with conn:
                    with conn.cursor() as cur:
                        query_data = """INSERT into useringroup VALUES
                                       (%s, %s)"""
                        cur.execute(query_data, [user_id, group_id])
                conn.close()

    except Exception as e:
        print(e)
        return {'status': "No Groups Found"}


def __get_course_id_from_group(group_id) -> int:
    conn = psycopg2.connect(dsn=get_conn_string())

    try:
        with conn:
            with conn.cursor() as cur:
                query_data = """SELECT course FROM
                                groups
                                WHERE group_id = %s """
                cur.execute(query_data, [group_id])
                data = cur.fetchone()

        if not data:
            raise Exception("No such group")
        return data[0]

    except Exception as e:
        print(e)
        return e


def add_user_to_course(user_id: int, course_id: int, user_role: Role) -> None:
    # TODO: Maybe add som check so admin or course teacher only can add people, mb need to take in the user doing the call
    conn = psycopg2.connect(dsn=get_conn_string())

    try:
        with conn:
            with conn.cursor() as cur:
                query_data = """INSERT into userincourse values
                                (%s, %s, %s)"""
                cur.execute(query_data, [user_id, course_id, user_role.name])
        conn.close()

    except Exception as e:
        print(e)
        return {'status': "Unable to add to course"}


def remove_user_from_group(user_id: int, group_id: int) -> None:
    # TODO: add some checks so not anyone can call this delete method, mb need to take in the user doing the call
    conn = psycopg2.connect(dsn=get_conn_string())

    try:
        with conn:
            with conn.cursor() as cur:
                query_data = """DELETE from useringroup
                                WHERE userid = %s AND groupid = %s """
                cur.execute(query_data, [user_id, group_id])

    except Exception as e:
        print(e)
        return {'status': "Could not remove from group"}


def is_teacher_on_course(user_id: int, course_id: int) -> bool:
    courses = get_courses_info(user_id)
    for course in courses:
        if course['courseID'] == course_id \
           and course['Role'] == Role.Teacher.name:
            return True

    return False


def is_admin_on_course(user_id: int, course_id: int) -> bool:
    courses = get_courses_info(user_id)
    for course in courses:
        if course['courseID'] == course_id \
           and course['Role'] == Role.Admin.name:
            return True

    return False


# TODO: include global role
def get_global_role(userId):
    print("return global role pls")


# TODO: add security checks, Course handler -> create/delete course, assignments, edit assignment details,