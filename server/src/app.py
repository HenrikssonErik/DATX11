

from typing import Literal
from flask import Flask, jsonify, make_response, request, send_file
from flask_cors import CORS
from .file_handler import handle_files, \
    handle_test_file, get_assignment_files_from_database
from .login_handler import user_registration, log_in, create_key,\
                            verify_and_get_id
from .user_handler import *
from .course_handler import *

# creating the Flask application
app = Flask(__name__)

CORS(app)
# creating private key for signing tokens
create_key()


def extract_token(request) -> str:
    cookies = request.headers.get('Cookies')
    if cookies:
        token = cookies.split('Token=')[1]
        return token
    return ""

@app.route('/login', methods=['POST'])
def login():
    password: str = request.form['password']
    email: str = request.form['email']
    data = log_in(email, password)
    res = make_response(jsonify(data[0]), data[1])
    return res


@app.route('/signUp', methods=['POST'])
def sign_up():
    response: tuple[dict[str, str], Literal[200, 400, 401, 406]] =\
        user_registration(request.form)

    # sign_up_response = {}
    # sign_up_response.update({'status': response[0]})
    res = make_response(response[0], response[1])
    return res


@app.route('/files', methods=['POST'])
def post_files():

    files = request.files.getlist('files')

    if not files:
        return "Files not found", 406
    res = handle_files(files)
    feedback_res = {}
    feedback_res.update({"feedback": res[0]})
    feedback_res.update(res[1])
    return make_response(jsonify(feedback_res), res[2])


@app.route('/unitTest', methods=['POST'])
def post_tests():
    print(request)
    files = request.files.getlist('files')

    if not files:
        return "Files not found", 406
    res = handle_test_file(files)
    return make_response(jsonify(res[0]), res[1])


@app.route('/getAssignmentFile', methods=['POST'])
def get_files():
    """
    Takes in information from the frontend about a specific course assignment
      file to then return its file content.
    Input data structure:
    { groupId: number, course: number, assignment: number, filename: string }
    Returns a file to be downloaded
    """
    data = request.get_json()
    group_id = data['groupId']
    course = data['course']
    assignment = data['assignment']
    filename = data['filename']  # should also be imported from frontend
    result = get_assignment_files_from_database(
        group_id, course, assignment, filename)

    res = make_response(send_file(path_or_file=result,
                                  download_name=filename, as_attachment=True))

    headers = {"Access-Control-Expose-Headers": "Content-Disposition",
               'Content-Disposition': 'attachment; filename={}'
               .format(filename)}
    res.headers = headers
    return res

@app.route('/getUserInfo', methods=['GET'])
def get_user_info():
    token = extract_token(request)
    user_id = verify_and_get_id(token)

    if (user_id):
        user_info = get_user(user_id)
        return make_response(jsonify(user_info), 200)
    else:
        return make_response("", 401)


@app.route('/getCourses', methods=['GET'])
def getCourses():
    """Returns an array of all Courses a user is associated with together with
       the following information: Role, CourseID, Course (abbriviation),
       Year, StudyPeriod
       Requires a token to be sent as a cookie with the request"""
    token = extract_token(request)
    user_id = verify_and_get_id(token)

    if (user_id):
        course_info: dict = {}
        course_info['Courses'] = get_courses_info(user_id)
        res = make_response(jsonify(course_info), 200)
        return res

    else:
        return make_response('', 401)


@app.route('/getGroup', methods=['GET'])
def getGroup():
    """Takes a Token as cookie, and a course_id.
    Returns the group_id, group_number and cid of members"""
    token = extract_token(request)
    user_id = verify_and_get_id(token)
    if (user_id):
        course = request.args.get('Course')
        group = get_group(user_id, course)
        return make_response(jsonify(group), 200)

    else:
        return make_response('', 401)


@app.route('/addToGroup', methods=['POST'])
def addToGroup():
    token = extract_token(request)
    request_user = verify_and_get_id(token)
    data = request.get_json()
    user_to_add: int = data['User']
    group_id:int = data['Group']
    course_id = data['Course']

    if(check_admin_or_course_teacher(request_user, course_id) or
       request_user == user_to_add):
        add_user_to_group(user_to_add, group_id)
        return make_response("", 200)
    return make_response ("", 401)


@app.route('/removeFromGroup', methods=['POST'])
def removeFromGroup():
    token = extract_token(request)
    request_user = verify_and_get_id(token)
    data = request.get_json()
    user_to_remove: int = data['User']
    group_id = data['Group']
    course_id = data['Course']

    if(check_admin_or_course_teacher(request_user, course_id) or
       request_user == user_to_remove):
        remove_user_from_group(user_to_remove, group_id)
        return make_response("", 200)
    return make_response ("", 401)


@app.route('/addToCourse', methods=['POST'])
def addToCourse():
    token = extract_token(request)
    request_user_id = verify_and_get_id(token)
    data = request.get_json()
    course_id: int = data['Course']
    user_to_add: int = data['User']
    role = data['Role']

    if (check_admin_or_course_teacher(request_user_id, course_id)):
            add_user_to_course(user_to_add, course_id, role)
            return make_response("", 200)
    return make_response("", 401)


@app.route('/removeFromCourse', methods=['POST'])
def removeFromCourse():
    token = extract_token(request)
    request_user_id = verify_and_get_id(token)
    data = request.get_json()
    course_id = data['Course']
    user_to_remove = data['User']

    if (check_admin_or_course_teacher(request_user_id, course_id)):
            remove_user_from_course(user_to_remove, course_id)
            return make_response("", 200)
    return make_response("", 401)


# TODO: wont work until global role is implemented
# HAVE NOT BEEN TESTED YET
@app.route('/createCourse', methods=['POST'])
def createCourse():
    token = extract_token(request)
    request_user_id = verify_and_get_id(token)
    data = request.get_json()
    course: str = data['Course']
    year: int = data['Year']
    lp: int = data['TeachingPeriod']
    groups: int = data['Groups']
    role = get_global_role(request_user_id)

    if (role == "Admin" or role == "Teacher"):
        course_id = create_course(course, year, lp)

        if (type(course_id) == tuple):
            return make_response(jsonify(course_id[0]), course_id[1])
        else:
            add_groups_to_course(groups, course_id)
            add_user_to_course(request_user_id, course_id, Role.Admin)
            return make_response(jsonify('Course Created'), 200)
    else:
        return make_response("Not allowed to create course", 401)

# TODO: remove course, getUser lists? (to add people), change user role, create assignment, edit assignment desc
