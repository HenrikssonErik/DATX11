

from typing import Literal
from flask import Flask, jsonify, make_response, request, send_file
from flask_cors import CORS
from .file_handler import handle_files, \
    handle_test_file, get_assignment_files_from_database
from .login_handler import user_registration, log_in, create_key, verify_and_get_id
from .user_handler import *
from .podman.podman_runner import init_images

# creating the Flask application
app = Flask(__name__)

CORS(app)
# init basic image
# init_images()
# creating private key for signing tokens
create_key()


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
    feedback_res.update(res[2])

    return make_response(jsonify(feedback_res), res[3])


@app.route('/unitTest', methods=['POST'])
def post_tests():
    print(request)
    files = request.files.getlist('files')

    if not files:
        return "Files not found", 406
    res = handle_test_file(files)
    return make_response(jsonify(res[0]), res[1])


# should be a post further on
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


@app.route('/getCourses', methods=['GET'])
def getCourses():
    """Returns an array of all Courses a user is associated with together with
       the following information: Role, CourseID, Course (abbriviation),
       Year, StudyPeriod
       Requires a token to be sent as a cookie with the request"""
    token = request.cookies.get('Token')
    user_id = verify_and_get_id(token)

    if (user_id):
        email = {'email': get_user_email(user_id)}
        course_info = get_courses_info(user_id)
        res = make_response(jsonify(email, course_info), 200)
        return res

    else:
        return make_response('', 401)


@app.route('/getGroup', methods=['GET'])
def getGroup():
    """Takes a Token as cookie, and a course_id.
    Returns the group_id, group_number and cid of members"""
    token = request.cookies.get('Token')
    user_id = verify_and_get_id(token)
    if (user_id):
        course = request.args.get('Course')
        group = get_group(user_id, course)
        return make_response(jsonify(group, 200))

    else:
        return make_response('', 401)

# TODO: check this
@app.route('/addToCourse', methods=['POST'])
def addToCourse():
    token = request.cookies.get('Token')
    request_user_id = verify_and_get_id(token)
    data = request.get_json()
    course_id = data['Course']
    user_to_add = data['User']

    if (check_admin_or_course_teacher(request_user_id, course_id)):
        add_user_to_course(user_to_add, course_id)

    return make_response("", 200)
