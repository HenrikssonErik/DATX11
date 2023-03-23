from .connector import get_conn_string
import psycopg2
from enum import Enum


class Role(Enum):
    Admin = 'Admin'
    Teacher = 'Teacher'
    Student = 'Student'


def get_assignments(course_id: int) -> tuple:
    conn = psycopg2.connect(dsn=get_conn_string())

    try:
        with conn:
            with conn.cursor() as cur:
                query_data = """SELECT assignment FROM assignments
                            WHERE courseid = %s"""
                cur.execute(query_data, [course_id])
                data =  [row[0] for row in cur.fetchall()]
                print(data)
        conn.close()
        if not data:
            return []
        # orderedData: dict[str, list] = []
        # orderedData.append({"Assignments": data})
        return data

    except Exception as e:
        print(e)
        return {'status': "No Courses Found"}


def get_user(user_id: int) -> dict:
    """Returns a dict with information on the user to the userId"""
    conn = psycopg2.connect(dsn=get_conn_string())

    try:
        with conn:
            with conn.cursor() as cur:
                query_data = """SELECT cid, email FROM Userdata
                            WHERE userid = %s"""
                cur.execute(query_data, (user_id,))
                data = cur.fetchone()
        conn.close()
        if not data:
            raise Exception("No such user")
        return {'cid': data[0], 'email': data[1]}

    except Exception as e:
        print(e)
        return {'status': "No User Found"}


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


def get_group(user_id: int, course_id: int) -> dict[str, str | list]:
    """Returns group ID and group number associated with the users group
        in the specified course"""
    conn = psycopg2.connect(dsn=get_conn_string())

    try:
        with conn:
            with conn.cursor() as cur:
                query_data = """SELECT groupid, groupnumber FROM
                                userGroupCourseInfo
                                WHERE userid = %s and courseid = %s"""
                cur.execute(query_data, (user_id, course_id))
                data = cur.fetchone()
        conn.close()

        if not data:
            raise Exception("No group for this user")

        orderedData: dict = {}
        orderedData["groupId"] = data[0]
        orderedData["groupNumber"] = data[1]
        group_members = __get_group_members(data[0])
        print(group_members)
        orderedData["groupMembers"] = group_members
        return orderedData

    except Exception as e:
        print(e)
        return {'status': "No Group Found"}


def __get_group_members(group_id: int) -> list:
    conn = psycopg2.connect(dsn=get_conn_string())
    try:
        with conn:
            with conn.cursor() as cur:
                query_data = """SELECT cid FROM usergroupinfo
                            WHERE groupid = %s"""
                cur.execute(query_data, [group_id])
                data = cur.fetchall()
        conn.close()
        if not data:
            raise Exception("No group members")
        userlist = []

        for user in data:
            userlist.append(user[0])
        return userlist

    except Exception as e:
        print(e)
        return {'status': "no_group_members"}


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
        return {'status': e.args}


def __get_course_id_from_group(group_id) -> int:
    conn = psycopg2.connect(dsn=get_conn_string())

    try:
        with conn:
            with conn.cursor() as cur:
                query_data = """SELECT course FROM
                                groups
                                WHERE groupid = %s """
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
                cur.execute(query_data, [user_id, course_id, user_role])
        conn.close()

    except Exception as e:
        print(e)
        return e


def remove_user_from_course(user_id: int, course_id) -> None:
    """Remove a User from the course"""
    conn = psycopg2.connect(dsn=get_conn_string())
    try:
        with conn:
            with conn.cursor() as cur:
                query_data = """Delete from userincourse where userid = %s AND courseid = %s"""
                cur.execute(query_data, [user_id, course_id])
        conn.close()

    except Exception as e:
        print(e)
        return (e)


def remove_user_from_group(user_id: int, group_id: int) -> None:
    # TODO: add some checks so not anyone can call this delete method, mb need to take in the user doing the call
    conn = psycopg2.connect(dsn=get_conn_string())

    try:
        with conn:
            with conn.cursor() as cur:
                query_data = """DELETE from useringroup
                                WHERE userid = %s AND groupid = %s """
                cur.execute(query_data, [user_id, group_id])
            conn.close()
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


def get_global_role(user_id) -> str:
    """Checks the gobal role for the user.
        Returns a string"""
    conn = psycopg2.connect(dsn=get_conn_string())

    try:
        with conn:
            with conn.cursor() as cur:
                query_data = """SELECT globalrole FROM userdata
                            WHERE userid = %s"""
                cur.execute(query_data, [user_id])
                data = cur.fetchone()
            conn.close()
        if not data:
            raise Exception("No such user")

        return data[0]

    except Exception as e:
        print(e)
        return {'status': "No User Found"}


# TODO: include global admin when implemented
def check_admin_or_course_teacher(user_id: int, course_id: int):
    course_administrator: bool = is_admin_on_course(user_id, course_id) or \
                            is_teacher_on_course(user_id, course_id)
    global_admin: bool = get_global_role(user_id) == Role.Admin.name

    return course_administrator or global_admin
