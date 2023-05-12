from .connector import get_conn_string
from . import course_handler
import psycopg2
from enum import Enum


class Role(Enum):
    """Enum for allowed Roles, both global and Course-roles"""
    Admin = 'Admin'
    Teacher = 'Teacher'
    Student = 'Student'


def get_user_ids_from_cids(cids: list[str]) -> tuple[list[int], list[str]]:
    """Returns a tuple of existing user_ids and none existing cids"""
    conn = psycopg2.connect(dsn=get_conn_string())
    with conn:
        with conn.cursor() as cur:
            query_data = """
            SELECT userid, chalmersId FROM userdata where chalmersId IN ({})
            """.format(",".join(['%s']*len(cids)))
            cur.execute(query_data, cids)
            res = cur.fetchall()
    conn.close()
    user_ids = [e[0] for e in res]

    not_user_cids = [] if len(cids) == len(res) \
        else list(set(cids).difference(e[1] for e in res))

    return (user_ids, not_user_cids)


def get_user(user_id: int) -> dict:
    """Returns a dict with information on the user to the userId"""
    conn = psycopg2.connect(dsn=get_conn_string())

    try:
        with conn:
            with conn.cursor() as cur:
                query_data = "SELECT chalmersId, userEmail, fullname FROM Userdata " +\
                    "WHERE userid = %s"
                cur.execute(query_data, (user_id,))
                data = cur.fetchone()
        conn.close()
        if not data:
            raise Exception("No such user")
        return {'cid': data[0], 'email': data[1], 'fullname': data[2],
                'id': user_id}

    except Exception as e:
        print(e)
        raise Exception("No user found") from e


def get_fullname(user_id: int) -> str:
    """Returns a string with information on the user's fullname"""
    conn = psycopg2.connect(dsn=get_conn_string())

    try:
        with conn:
            with conn.cursor() as cur:
                query_data = "SELECT fullname FROM Userdata " +\
                    "WHERE userid = %s"
                cur.execute(query_data, [user_id])
                data = cur.fetchone()
        conn.close()
        if data is None:
            raise Exception("No such user")
        return data[0]

    except Exception as e:
        print(e)
        raise Exception("No user found") from e


def get_group(user_id: int, course_id: int) -> dict[str, str | list]:
    """Returns group ID and group number associated with the users group
        in the specified course"""
    conn = psycopg2.connect(dsn=get_conn_string())

    try:
        with conn:
            with conn.cursor() as cur:
                query_data = "SELECT groupid, groupnumber FROM " +\
                    "userGroupCourseInfo " +\
                    "WHERE userid = %s and courseid = %s"
                cur.execute(query_data, (user_id, course_id))
                data = cur.fetchone()
        conn.close()

        if not data:
            raise Exception("No group for this user")

        ordered_data: dict = {}
        ordered_data["groupId"] = data[0]
        ordered_data["groupNumber"] = data[1]
        group_members = _get_group_members(data[0])
        ordered_data["groupMembers"] = group_members
        return ordered_data

    except Exception as e:
        print(e)
        raise Exception("No group found") from e


def _get_group_members(group_id: int) -> list:
    """ Internal method to retrieve all members of a group"""
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
        raise Exception(
            "Something went wrong when getting group members") from e


def add_user_to_group(user_id: int, group_id: int) -> None:
    """Adds a user to the specified group, also checks that th euser is
    part of the course to which the group is associated"""
    user_courses = course_handler.get_courses_info(user_id)
    conn = psycopg2.connect(dsn=get_conn_string())

    course_id = _get_course_id_from_group(group_id)

    try:
        for course in user_courses:
            if course['courseID'] == course_id and \
               course['Role'] == Role.Student.name:
                with conn:
                    with conn.cursor() as cur:
                        query_one = """SELECT EXISTS(SELECT 1 FROM
                        usergroupcourseinfo WHERE courseid=%s AND userid=%s) as
                        exists_row;"""
                        cur.execute(query_one, [course_id, user_id])
                        in_group = cur.fetchone()[0]
                        if not (in_group):
                            query_two = """INSERT into useringroup VALUES
                                           (%s, %s)"""
                            cur.execute(query_two, [user_id, group_id])
                        else:
                            raise Exception("Already in group")
                conn.close()

    except Exception as e:
        print(e)
        raise Exception("Error when adding user!") from e


def _get_course_id_from_group(group_id) -> int:
    """Returns a groups associated course, only ment for internal use"""
    conn = psycopg2.connect(dsn=get_conn_string())

    try:
        with conn:
            with conn.cursor() as cur:
                query_data = """SELECT course FROM
                                groups
                                WHERE groupid = %s """
                cur.execute(query_data, [group_id])
                data = cur.fetchone()
        conn.close()
        if not data:
            raise Exception("No such group")
        return data[0]

    except Exception as e:
        print(e)
        raise Exception("Error when getting course id!") from e


def add_users_to_course(user_ids: list[int], course_id: int):
    """Adds all the users in `user_ids` to the specified course"""
    if len(user_ids) > 0:
        conn = psycopg2.connect(dsn=get_conn_string())
        try:
            with conn:
                with conn.cursor() as cur:
                    query_data = "insert into userincourse values " + \
                        "(%s,%s,%s) on conflict do nothing;"

                    for id in user_ids:
                        cur.execute(query_data, [id, course_id, 'Student'])
        except psycopg2.IntegrityError as e:
            raise \
                Exception(
                    f"Could not add users {user_ids} to course {course_id} "
                    "because either the course or a student do not exist"
                ) from e
        except Exception as e:
            raise \
                Exception(
                    f"Could not add users {user_ids} to course {course_id}"
                ) from e
        finally:
            conn.close()


def add_user_to_course(user_id: int, course_id: int, user_role: Role) -> None:
    """Adds the specified user to a course and assigns it a course role"""
    conn = psycopg2.connect(dsn=get_conn_string())
    try:
        with conn:
            with conn.cursor() as cur:
                query_data = "INSERT into userincourse values " +\
                    "(%s, %s, %s)"
                cur.execute(query_data, [user_id, course_id, user_role.name])
        conn.close()

    except Exception as e:
        print(e)
        raise Exception("Error when adding user to course!") from e


def remove_user_from_course(user_id: int, course_id) -> None:
    """Remove a User from the course"""
    conn = psycopg2.connect(dsn=get_conn_string())
    try:
        with conn:
            with conn.cursor() as cur:
                query_data = """Delete from userincourse where userid = %s AND
                courseid = %s"""
                cur.execute(query_data, [user_id, course_id])
        conn.close()

    except Exception as e:
        print(e)
        raise Exception("Error when removing user from course!") from e


def remove_user_from_group(user_id: int, group_id: int) -> None:
    """Removes a User from a group"""
    conn = psycopg2.connect(dsn=get_conn_string())

    try:
        with conn:
            with conn.cursor() as cur:
                query_data = """DELETE from useringroup
                                WHERE userid = %s AND groupid = %s """
                cur.execute(query_data, [user_id, group_id])
                query_two = """SELECT (fullname IS NULL)
                AS is_empty FROM GroupDetails WHERE groupid = %s;"""
                cur.execute(query_two, [group_id])
                emptyGroup: bool = cur.fetchone()[0]
                if (emptyGroup):
                    query_three = """delete from groups where groupid = %s """
                    cur.execute(query_three, [group_id])
        conn.close()
    except Exception as e:
        print(e)
        raise Exception("Error when removing user from group!") from e


def is_teacher_on_course(user_id: int, course_id: int) -> bool:
    """Checks if a user has the teacher role on the course
    Returns True/False"""
    courses = course_handler.get_courses_info(user_id)
    for course in courses:
        if course['courseID'] == course_id \
           and course['Role'] == Role.Teacher.name:
            return True

    return False


def is_in_course(user_id: int, course_id: int) -> bool:
    """Checks if a user is a member of the course
    Returns True/False"""
    courses = course_handler.get_courses_info(user_id)
    for course in courses:
        if (course['courseID'] == course_id):
            return True
    return False


def is_admin_on_course(user_id: int, course_id: int) -> bool:
    """Checks if a user has the Admin role on the course
    Returns True/False"""
    courses = course_handler.get_courses_info(user_id)
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
                query_data = "SELECT globalrole FROM userdata " + \
                    "WHERE userid = %s"
                cur.execute(query_data, [user_id])
                data = cur.fetchone()
        conn.close()
        if not data:
            raise Exception("No such user")

        return data[0]

    except Exception as e:
        print(e)
        raise Exception("Error when finding the user!") from e


def check_admin_or_course_teacher(user_id: int, course_id: int):
    course_administrator: bool = is_admin_on_course(user_id, course_id) or \
        is_teacher_on_course(user_id, course_id)
    global_admin: bool = get_global_role(user_id) == Role.Admin.name

    return course_administrator or global_admin


def change_role_on_course(new_role: str, user_id: int,
                          course_id: int) -> dict | None:
    """Changes a users role on the specified course"""
    conn = psycopg2.connect(dsn=get_conn_string())

    if (new_role in [role.name for role in Role]):
        try:
            with conn:
                with conn.cursor() as cur:
                    query_data = """UPDATE userincourse SET userrole = %s
                    WHERE userid = %s AND courseid = %s;"""
                    cur.execute(query_data, [new_role, user_id, course_id])
            conn.close()
        except Exception as e:
            print(e)
            raise Exception("Could not change the role") from e
        return None
    else:
        return {'status': "Not an allowed role"}


def get_users_on_course(course: int) -> tuple:
    """Returns a list of all users associated with a course and their
    course role"""
    conn = psycopg2.connect(dsn=get_conn_string())

    try:
        with conn:
            with conn.cursor() as cur:
                query_data = """SELECT userdata.userid, userdata.chalmersId,
                userdata.fullname, userdata.userEmail, userincourse.userrole
                FROM public.userdata
                JOIN public.userincourse ON
                userdata.userid = userincourse.userid
                WHERE userincourse.courseid = %s;"""
                cur.execute(query_data, [course])
                data = cur.fetchall()
        conn.close()
        if not data:
            return [], 200

        users: list[dict] = []
        for user in data:
            users.append({'id': user[0], 'cid': user[1], 'fullname': user[2],
                          'email': user[3], 'role': user[4]})
        return users, 200

    except Exception as e:
        print(e)
        raise Exception("Could not get users in course") from e
