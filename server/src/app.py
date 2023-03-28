

from typing import Literal
from flask import Flask, jsonify, make_response, request, send_file
from flask_cors import CORS
from .file_handler import handle_files, \
    handle_test_file, get_assignment_files_from_database
from .login_handler import user_registration, log_in, create_key,\
                            verify_and_get_id
from .user_handler import *
from .course_handler import *
from .podman.podman_runner import init_images

# creating the Flask application
app = Flask(__name__)

CORS(app)
# init basic image
# init_images()
# creating private key for signing tokens
create_key()


def extract_token(request) -> str:
    cookies = request.headers.get('Cookies')
    if cookies:
        token = cookies.split('Token=')[1]
        return token
    return ""


@app.route('/login', methods=['POST'])
def logIn():
    password: str = request.form['password']
    email: str = request.form['email']
    data = log_in(email, password)
    res = make_response(jsonify(data[0]), data[1])
    return res


@app.route('/signUp', methods=['POST'])
def signUp():
    response: tuple[dict[str, str], Literal[200, 400, 401, 406]] =\
        user_registration(request.form)

    # sign_up_response = {}
    # sign_up_response.update({'status': response[0]})
    res = make_response(response[0], response[1])
    return res


@app.route('/files', methods=['POST'])
def postFiles():

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
def postTests():
    print(request)
    files = request.files.getlist('files')

    if not files:
        return "Files not found", 406
    res = handle_test_file(files)
    return make_response(jsonify(res[0]), res[1])


@app.route('/getAssignmentFile', methods=['POST'])
def getFiles():
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
def getUserInfo():
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
        course_info['courses'] = get_courses_info(user_id)
        res = make_response(jsonify(course_info), 200)
        return res

    else:
        return make_response('', 401)


@app.rout('/getCourse', methods=['GET'])
def getCourse():
    token = extract_token(request)
    user_id = verify_and_get_id(token)
    course_id = request.args.get('Course')

    if (user_id):
        course = get_course_info(user_id, course_id)
        return make_response(jsonify(course), 200)
    else:
        return make_response("", 401)


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
    group_id: int = data['Group']
    course_id = data['Course']

    if (check_admin_or_course_teacher(request_user, course_id) or
       request_user == user_to_add):
        add_user_to_group(user_to_add, group_id)
        return make_response("", 200)
    return make_response("", 401)


@app.route('/removeFromGroup', methods=['POST'])
def removeFromGroup():
    token = extract_token(request)
    request_user = verify_and_get_id(token)
    data = request.get_json()
    user_to_remove: int = data['User']
    group_id = data['Group']
    course_id = data['Course']

    if (check_admin_or_course_teacher(request_user, course_id) or
       request_user == user_to_remove):
        remove_user_from_group(user_to_remove, group_id)
        return make_response("", 200)
    return make_response("", 401)


# Should probably be redone to take a list of users, redo how singup works
# as well with cid/email being added to the list first
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


@app.route('/createAssignment', method=['POST'])
def createAssignment():
    token = extract_token(request)
    request_user_id = verify_and_get_id(token)
    data = request.get_json()
    course_id = data['Course']
    description = data.get('Description', "")
    end_date = data['Date']
    assignment_nr = data['AssignmentNr']
    file_names = data.get('FileNames', [])

    if (check_admin_or_course_teacher(request_user_id, course_id)):
        res = create_assignment(course_id, description, assignment_nr,
                                end_date, file_names)
        if not (len(res) == 0):
            return make_response(jsonify(res), 400)
        else:
            make_response("", 200)


@app.route('/changeUserRole', methods=['POST'])
def changeUserRole():
    """Course admins can call this method to change a users role in a course.
        E.g from Student to TA (Teacher)
        Returns: Status Code 200, 401"""
    token = extract_token(request)
    request_user_id = verify_and_get_id(token)
    data = request.get_json()
    course = data['Course']
    user_to_change = data['User']
    new_role = data['Role']
    # TODO: check so user dont change theri own role
    if (is_admin_on_course(request_user_id, course)):
        res = change_role_on_course(new_role, user_to_change, course)

        if res is not None:
            return make_response(jsonify(res), 401)

        return make_response("", 200)
    return make_response({"status": 'Only course admins can change roles'},
                         401)
# TODO: remove course? mb not?, getGroupsInCourse, getUsersInCourse lists ? (to add people),
#  edit assignment desc, edit assignment enddate

@app.route('/editDescription', methods=['POST'])
def editDesc():
    token = extract_token(request)
    request_user_id = verify_and_get_id(token)
    data = request.get_json()
    new_desc = data['Desc']
    course = data['Course']
    assignment = data['Assignment']

    if (check_admin_or_course_teacher(request_user_id, course)):
        res = change_descirption(new_desc, course, assignment)

        if res is None:
            return make_response("", 200)
        else:
            return make_response(jsonify(res), 401)
    else:
        return make_response(jsonify({'status': 'Not a course teacher'}), 401)
