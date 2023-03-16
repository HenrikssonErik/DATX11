from .connector import get_conn_string
import psycopg2
from enum import Enum


class Role(Enum):
    Admin = 'Admin'
    Teacher = 'Teacher'
    Student = 'Student'


def get_courses(userId: int) -> list[dict[str, any]]:
    conn = psycopg2.connect(dsn=get_conn_string())

    try:
        with conn:
            with conn.cursor() as cur:
                query_data = """SELECT * FROM User_course_info
                            WHERE userid = %s"""
                cur.execute(query_data, (userId,))
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
        return {'status': "No Courses Found"}, 401


def get_group(userId: int, courseId: int) -> dict[str, str]:
    conn = psycopg2.connect(dsn=get_conn_string())

    try:
        with conn:
            with conn.cursor() as cur:
                query_data = """SELECT groupid, groupnumber FROM
                                user_group_course_info
                                WHERE userid = %s and courseid = %s"""
                cur.execute(query_data, (userId, courseId))
                data = cur.fetchone()
        conn.close()

        if not data:
            raise Exception("No groups for this user")

        orderedData: dict = {}
        orderedData["groupid"] = data[0]
        orderedData["groupNumber"] = data[1]
        return orderedData

    except Exception as e:
        print(e)
        return {'status': "No Groups Found"}, 401

# TODO: fill in the blanks :)


def add_user_to_group(userId: int, groupId: int):
    # check user on course and group on the course
    user_courses = get_courses(userId)
    conn = psycopg2.connect(dsn=get_conn_string())

    course_id = __get_courseId_from_group(groupId)

    # add to group
    try:
        for course in user_courses:
            if course['courseID'] == course_id and \
               course['Role'] == Role.Student.name:
                with conn:
                    with conn.cursor() as cur:
                        query_data = """INSERT into useringroup VALUES
                                       (%s, %s)"""
                        cur.execute(query_data, [userId, groupId])
                conn.close()

    except Exception as e:
        print(e)
        return {'status': "No Groups Found"}, 401


def __get_courseId_from_group(groupId) -> int:
    conn = psycopg2.connect(dsn=get_conn_string())

    try:
        with conn:
            with conn.cursor() as cur:
                query_data = """SELECT course FROM
                                groups
                                WHERE groupid = %s """
                cur.execute(query_data, [groupId])
                data = cur.fetchone()

        if not data:
            raise Exception("No such group")
        return data[0]

    except Exception as e:
        print(e)
        return {'status': "No Course to match the group"}, 401

def add_user_to_course(userId: int, courseId: int, userRole: Role):
    # check user on course
    # check group on courseä
    # add to group
    print("heh")


def remove_user_from_group(userId: int, groupId: int):
    # do the doings
    print("heh")
