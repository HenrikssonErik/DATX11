from .connector import get_conn_string
import psycopg2


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
        return {'error': "No Courses Found"}, 401
