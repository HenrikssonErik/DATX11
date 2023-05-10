

import jwt
from flask_mail import Mail, Message
from typing import Literal
from flask import Flask, Response, jsonify, make_response, render_template, \
    request, send_file
from flask_cors import CORS
from .constants import DOMAIN
from .file_handler import handle_files, \
    handle_test_file, get_assignment_file_from_database, get_test_filenames,\
    get_test_file, get_filenames
from . import user_handler
from . import course_handler
from .login_handler import new_password, user_registration, log_in, \
    create_key, user_to_resend_verification_email, \
    user_to_send_reset_pwd_email, verify_and_get_cid, verify_and_get_id, \
    create_temp_users
# from .podman.podman_runner import init_images

# init basic image
# init_images()

# creating the Flask application
app = Flask(__name__)
CORS(app)
mail = Mail(app)

app.config.from_pyfile('mailconfig.cfg')

mail = Mail(app)


# creating private key for signing tokens
create_key()


def extract_token(request) -> str | None:
    cookies = request.headers.get('Cookies')
    if cookies is not None:
        separated_cookies = cookies.split('; ')
        for cookie in separated_cookies:
            name, value = cookie.split('=')
            if name == 'Token':
                return value
    return None


@app.route('/login', methods=['POST'])
def login():
    password: str = request.form['password']
    email: str = request.form['email']
    data = log_in(email, password)
    res = make_response(jsonify(data[0]), data[1])
    return res


@app.route('/signUp', methods=['POST'])
def sign_up() -> Response:
    """Signs the user up to the database. If the data is validated in
    the backend, we send a verification email via the
    send_verification_email-function.

    Returns:
        Response: An HTTP-Response containing of the status
        from login_handler's user_registration-function,
        either successful or invalidated.
    """
    response: tuple[dict[str, str], Literal[200, 400, 401, 406, 500]] =\
        user_registration(request.form)
    if (response[1] == 200):
        send_verification_email(
            request.form['email'], response[0]['token'])
        res = make_response({'status': 'success'}, response[1])
    else:
        res = make_response(response[0], response[1])

    return res


@app.route('/resendVerification', methods=['POST'])
def resend_verification_email() -> Response:
    data = request.form
    cid = data['cid']

    user_lookup = user_to_resend_verification_email(cid)
    if (user_lookup[1] == 200):
        email = user_lookup[0]['email']
        token = user_lookup[0]['token']
        send_verification_email(email, token)
        return make_response({'status': "success"}, 200)
    else:
        return make_response(user_lookup)


@app.route('/reset_pwd_email', methods=['POST'])
def reset_pwd() -> Response:
    data = request.form
    cid = data['cid']

    user_lookup = user_to_send_reset_pwd_email(cid)

    if (user_lookup[1] == 200):
        email = user_lookup[0]['email']
        token = user_lookup[0]['token']
        send_forgotpwd_email(email, token)
        return make_response({'status': "success"}, 200)
    else:
        return make_response(user_lookup)


@app.route('/verify_email', methods=['POST'])
def verify_email() -> Response:
    """
    This function will be routed to whenever a verification,
    including a verification token in clicked.
    This will verify the user, if possible, otherwise; return
    the appropriate error message to the frontend to be displayed.

    Returns:
        Response: An HTTP-Response containing either:

        {'status': status_message}, status_code
        OR:
        {'cid': user's cid(will be got from the token)}, 200
    """
    data = request.get_json()
    token = data['token']

    try:
        verify: tuple[dict[str, str],
                      Literal[200, 406, 500]] = \
            verify_and_get_cid(token)
        response = make_response(verify)
        return response
    except jwt.ExpiredSignatureError:
        res = make_response({'status': 'expired_verification_signature'}, 400)
        return res
    except jwt.InvalidTokenError:
        res = make_response({'status': 'invalid_verification_token'}, 400)
        return res


@app.route('/new_pwd', methods=['POST'])
def update_password() -> Response:
    data = request.form
    token: str = data['token']
    password: str = data['password']
    verification_password: str = data['verificationPassword']

    try:
        token_verification = verify_and_get_cid(token)
    except Exception as e:
        print(e)
        return make_response({"status": "error"}, 400)

    if not token_verification[1] == 200:
        return make_response(token_verification)

    if not password == verification_password:
        return make_response({"status": "not_matching_password"}, 400)

    cid: str = token_verification[0]['cid']

    password_status = new_password(cid, password)

    return make_response(password_status)


def send_forgotpwd_email(to: str, token: str) -> None:
    """
    Sends a forgot password email to a user.
    This email is in an HTML format, with a working link sending
    the user directly to the correct endpoint in the frontend
    (To be updated whenever the website is launched to not link to localhost)


    Args:
        to (str): The recipient's email address, which has been verified
        in login_handler's check_data_input to be a valid email.
        token_dict (dict): The jwt-generated token from login_handler's
        create_verification_token-function.
    """

    msg = Message('Forgot password?',
                  sender='temphydrant@gmail.com', recipients=[to])

    endpoint: str = "/forgotPwd/" + token

    url: str = DOMAIN + endpoint

    msg.html = render_template("forgotPwdTemplate.html", link=url, raw_url=url)

    mail.send(msg)


def send_verification_email(to: str, token: str) -> None:
    """
    Sends a verification email to the specific user signing up.
    This email is in an HTML format, with a working link sending
    the user directly to the correct endpoint in the frontend
    (To be updated whenever the website is launched to not link to localhost)


    Args:
        to (str): The recipient's email address, which has been verified
        in login_handler's check_data_input to be a valid email.
        token_dict (dict): The jwt-generated token from login_handler's
        create_verification_token-function.
    """
    msg = Message('Verification Email for Hydrant',
                  sender='temphydrant@gmail.com', recipients=[to])

    endpoint: str = "/verifyEmail/" + token

    url: str = DOMAIN + endpoint

    msg.html = render_template("emailTemplate.html", link=url, raw_url=url)

    mail.send(msg)


# Upload assignment files to get tested
@app.route('/files', methods=['POST'])
def post_files():
    token = extract_token(request)
    user_id: int = verify_and_get_id(token)
    files = request.files.getlist('files')
    course_id: int = int(request.form['Course'])
    group_id: int = int(request.form['Group'])
    assignment_nr: int = int(request.form['Assignment'])

    if not files:
        return "Files not found", 406
    if (user_id):
        if (group_id == user_handler.get_group(user_id,
                                               course_id)["groupId"]):
            if not (course_handler.passed_deadline(course_id, assignment_nr)):
                res = handle_files(files, course_id, group_id, assignment_nr)
                feedback_res = {}
                feedback_res.update({"feedback": res[0]})
                feedback_res.update(res[1])
                return make_response(jsonify(feedback_res), res[3])
            else:
                return make_response({'status': 'deadline_passed'}, 400)
        else:
            return make_response({'status': 'not_in_group'}, 401)
    else:
        return make_response({'status': 'not_logged_in'}, 401)


@app.route('/unitTest', methods=['POST'])
def post_tests():
    token = extract_token(request)
    user_id: int = verify_and_get_id(token)
    files = request.files.getlist('files')
    course = int(request.form['Course'])
    assignment = int(request.form['Assignment'])

    if (user_handler.check_admin_or_course_teacher(user_id, course)):

        if not files:
            return "Files not found", 406

    if (user_handler.check_admin_or_course_teacher(user_id, course)):
        res = handle_test_file(files, course, assignment)
        return make_response(jsonify(res[0]), res[1])
    else:
        return make_response("", 401)


"""
@app.route('/getAssignmentTestFeedback', methods=['POST'])
def get_assignment_feedback():
    data = request.get_json()
    group_id = data['groupId']
    course = data['course']
    assignment = data['assignment']
    (result, code) = get_assignment_test_feedback_from_database(
        course,
        assignment,
        group_id
    )
    if code == 200:
        return make_response(result, 200)
    else:
        return make_response("", code)
"""


@app.route('/getAssignmentFile', methods=['GET'])
def get_file():
    """
    Takes in information from the frontend about a specific course assignment
      file to then return its file content.
    Input data structure:
    { groupId: number, course: number, assignment: number, filename: string }
    Returns a file to be downloaded
    """
    token = extract_token(request)
    user_id: int = verify_and_get_id(token)

    data = request.args
    group_id = int(data['groupId'])
    course = int(data['course'])
    assignment = int(data['assignment'])
    filename = data['filename']
    submission = int(data['submission'])
    headers = {"Access-Control-Expose-Headers": "Content-Disposition",
               'Content-Disposition': 'attachment; filename={}'
               .format(filename)}

    if (user_handler.check_admin_or_course_teacher(user_id, course) or
       user_handler.get_group(user_id, course)['groupId'] == group_id):

        result = get_assignment_file_from_database(
            group_id, course, assignment, filename, submission)

        res = make_response(send_file(path_or_file=result,
                                      download_name=filename,
                                      as_attachment=True))

        res.headers = headers
        return res
    else:
        return make_response({'status': 'No_Access'}, 401)


@app.route('/DownloadTestFile', methods=['POST'])
def get_tests():
    """
    Takes in information from the frontend about a specific course assignment
      test file to then return its file content.
    Input data structure:
    Returns a file to be downloaded
    """
    token = extract_token(request)
    user_id: int = verify_and_get_id(token)

    data = request.get_json()
    course = int(data['course'])
    assignment = int(data['assignment'])
    filename = data['filename']
    headers = {"Access-Control-Expose-Headers": "Content-Disposition",
               'Content-Disposition': 'attachment; filename={}'
               .format(filename)}

    if (user_handler.check_admin_or_course_teacher(user_id, course)):

        result = get_test_file(course, assignment, filename)

        res = make_response(send_file(path_or_file=result,
                                      download_name=filename,
                                      as_attachment=True))

        res.headers = headers
        return res
    return make_response({'status': 'No_Access'}, 401)


@app.route('/getUserInfo', methods=['GET'])
def get_user_info():
    token = extract_token(request)
    user_id = verify_and_get_id(token)

    if (user_id):
        user_info = user_handler.get_user(user_id)
        return make_response(jsonify(user_info), 200)
    else:
        return make_response("", 401)


@app.route('/getCourses', methods=['GET'])
def get_courses():
    """Returns an array of all Courses a user is associated with together with
       the following information: Role, CourseID, Course (abbriviation),
       Year, StudyPeriod
       Requires a token to be sent as a cookie with the request"""
    token = extract_token(request)
    user_id = verify_and_get_id(token)

    if (user_id):
        course_info: dict = {}
        course_info['courses'] = course_handler.get_courses_info(user_id)
        res = make_response(jsonify(course_info), 200)
        return res

    else:
        return make_response('', 401)


@app.route('/getCourse', methods=['GET'])
def get_course():
    token = extract_token(request)
    user_id = verify_and_get_id(token)
    course_id = request.args.get('Course')

    if (user_id):
        course = course_handler.get_course_info(user_id, course_id)
        return make_response(jsonify(course), 200)
    else:
        return make_response("", 401)


@app.route('/getMyGroup', methods=['GET'])
def get_my_group():
    """Takes a Token as cookie, and a course_id.
    Returns the group_id, group_number and cid of members"""
    token = extract_token(request)
    user_id = verify_and_get_id(token)
    if (user_id):
        course = request.args.get('Course')
        group = user_handler.get_group(user_id, course)
        return make_response(jsonify(group), 200)

    else:
        return make_response('', 401)


@app.route('/addToGroup', methods=['POST'])
def add_to_group():
    token = extract_token(request)
    request_user = verify_and_get_id(token)
    data = request.get_json()
    user_to_add: int = data['User']
    group_id: int = data['Group']
    course_id = data['Course']

    if (user_handler.check_admin_or_course_teacher(request_user, course_id) or
       request_user == user_to_add):
        user_handler.add_user_to_group(user_to_add, group_id)
        return make_response("", 200)
    return make_response("", 401)


@app.route('/removeFromGroup', methods=['POST'])
def remove_from_group():
    token = extract_token(request)
    request_user = verify_and_get_id(token)
    data = request.get_json()
    user_to_remove: int = data['User']
    group_id = data['Group']
    course_id = data['Course']

    if (user_handler.check_admin_or_course_teacher(request_user, course_id) or
       request_user == user_to_remove):
        user_handler.remove_user_from_group(user_to_remove, group_id)
        return make_response("", 200)
    return make_response("", 401)


@app.route('/batchAddToCourse', methods=['POST'])
def batch_add_to_course():
    """
    Gets a list of cids that needs to be added to a course and
    in the case of the user not existing, the user should be created
    with a random temp password.
    """
    token = extract_token(request)
    if token is None:
        return make_response("Missing token", 401)
    try:
        request_user_id = verify_and_get_id(token)
    except jwt.InvalidTokenError:
        return make_response("Invalid token", 400)
    data = request.get_json()
    course_id: int = data['Course']
    if not (user_handler.check_admin_or_course_teacher(
        request_user_id,
        course_id
    )):
        return make_response("", 401)

    (user_ids, none_existing_cids) = \
        user_handler.get_user_ids_from_cids(data["Cids"])
    user_handler.add_users_to_course(user_ids, course_id)

    if len(none_existing_cids) != 0:
        newly_registered_cids = create_temp_users(none_existing_cids)
        (user_ids, _) = \
            user_handler.get_user_ids_from_cids(newly_registered_cids)
        user_handler.add_users_to_course(user_ids, course_id)
    return make_response("", 200)


# Should probably be redone to take a list of users, redo how singup works
# as well with cid/email being added to the list first
@app.route('/addToCourse', methods=['POST'])
def add_to_course():
    token = extract_token(request)
    request_user_id = verify_and_get_id(token)
    data = request.get_json()
    course_id: int = data['Course']
    user_to_add: int = data['User']
    role = data['Role']

    if (user_handler.check_admin_or_course_teacher(
        request_user_id,
        course_id
    )):
        user_handler.add_user_to_course(user_to_add, course_id, role)
        return make_response("", 200)
    return make_response("", 401)


@app.route('/removeFromCourse', methods=['POST'])
def remove_from_course():
    token = extract_token(request)
    request_user_id = verify_and_get_id(token)
    data = request.get_json()
    course_id = data['Course']
    user_to_remove = data['User']

    if (user_handler.check_admin_or_course_teacher(request_user_id,
                                                   course_id)):
        user_handler.remove_user_from_course(user_to_remove, course_id)
        return make_response("", 200)
    return make_response("", 401)


@app.route('/createCourse', methods=['POST'])
def create_course():
    token = extract_token(request)
    request_user_id = verify_and_get_id(token)
    data = request.get_json()
    course: str = data['Course']
    year: int = data['Year']
    lp: int = data['TeachingPeriod']
    abbreviation: str = data['Abbreviation']
    role = user_handler.get_global_role(request_user_id)

    if (role == "Admin" or role == "Teacher"):
        course_id = course_handler.create_course(course, abbreviation, year,
                                                 lp)

        if (type(course_id) == tuple):
            return make_response(jsonify(course_id[0]), course_id[1])
        else:
            user_handler.add_user_to_course(request_user_id, course_id,
                                            user_handler.Role.Admin)
            return make_response(jsonify('Course Created'), 200)
    else:
        return make_response("Not allowed to create course", 401)


@app.route('/createGroup', methods=['POST'])
def create_group():
    """Creates a group for the specified course and adds the user to it"""
    token = extract_token(request)
    user_id = verify_and_get_id(token)
    data = request.get_json()
    course_id = data['Course']

    if (user_id):
        if (user_handler.is_in_course(user_id, course_id)):
            course_handler.add_group_to_course(course_id, user_id)
            return make_response("", 200)
        else:
            return make_response({'status': 'not_in_course'}, 401)
    else:
        return make_response({'status': 'not_in_course'}, 401)


@app.route('/createAssignment', methods=['POST'])
def create_assignment():
    token = extract_token(request)
    request_user_id = verify_and_get_id(token)
    data = request.get_json()
    course_id = data['Course']
    description = data.get('Description', "")
    end_date = data['Date']
    file_names = data.get('fileNames', [])
    assignment_name = data.get('AssignmentName')
    max_score = data.get('MaxScore')
    pass_score = data.get('PassScore')

    if (user_handler.check_admin_or_course_teacher(request_user_id,
                                                   course_id)):
        res = course_handler.create_assignment(course_id, description,
                                               assignment_name, end_date,
                                               file_names, max_score,
                                               pass_score)
        if not (len(res) == 0):
            return make_response(jsonify(res), 400)
        else:
            return make_response("", 200)
        
    return make_response({'status': 'No_Access'}, 401)
    


@app.route('/changeUserRole', methods=['POST'])
def change_user_role():
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
    if (user_handler.is_admin_on_course(request_user_id, course)):
        res = user_handler.change_role_on_course(new_role, user_to_change,
                                                 course)

        if res is not None:
            return make_response(jsonify(res), 401)

        return make_response("", 200)
    return make_response({"status": 'Only course admins can change roles'},
                         401)


@app.route('/editDescription', methods=['POST'])
def edit_desc():
    token = extract_token(request)
    request_user_id = verify_and_get_id(token)
    data = request.form
    new_desc = data['Desc']
    course = int(data['Course'])
    assignment = int(data['Assignment'])

    if (user_handler.check_admin_or_course_teacher(request_user_id, course)):
        res = course_handler.change_description(new_desc, course, assignment)

        if res is None:
            return make_response("", 200)
        else:
            return make_response(jsonify(res), 401)
    else:
        return make_response(jsonify({'status': 'Not a course teacher'}), 401)


@app.route('/editAssignmentName', methods=['POST'])
def edit_name():
    token = extract_token(request)
    request_user_id = verify_and_get_id(token)
    data = request.form
    new_name = data['Name']
    course = int(data['Course'])
    assignment = int(data['Assignment'])

    if (user_handler.check_admin_or_course_teacher(request_user_id, course)):
        res = course_handler.change_assignment_name(
            new_name, course, assignment)

        if res is None:
            return make_response("", 200)
        else:
            return make_response(jsonify(res), 401)
    else:
        return make_response(jsonify({'status': 'Not a course teacher'}), 401)


@app.route('/getUsersInCourse', methods=['GET'])
def get_users_in_course():
    token = extract_token(request)
    request_user_id = verify_and_get_id(token)
    course = int(request.args.get('Course'))
    if (user_handler.is_admin_on_course(request_user_id, course)):
        res = user_handler.get_users_on_course(course)
        return make_response(jsonify({"Users": res[0]}), res[1])
    else:
        return make_response("", 401)


@app.route('/changeAssignmentDate', methods=['POST'])
def change_assignment_date():
    token = extract_token(request)
    request_user_id = verify_and_get_id(token)
    data = request.form
    course: int = int(data['Course'])
    assignment: int = int(data['Assignment'])
    new_date: str = data['Date']

    if (user_handler.check_admin_or_course_teacher(request_user_id, course)):
        res = course_handler.change_end_date(course, assignment, new_date)

        if res is None:
            return make_response("", 200)
        else:
            return make_response(jsonify(res), 401)
    else:
        return make_response(jsonify({'status': 'Not a course teacher'}), 401)


@app.route('/getFeedback', methods=['GET'])
def get_feedback():
    token = extract_token(request)
    user_id = verify_and_get_id(token)
    course = int(request.args.get('Course'))
    assignment = int(request.args.get('Assignment'))

    if (user_id):
        group = user_handler.get_group(user_id, course)['groupId']
        feedback = course_handler.get_assignment_feedback(course, assignment,
                                                          group)
        return make_response(jsonify(feedback), 200)

    else:
        return make_response({"status": 'not_logged_in'}, 401)


@app.route('/getTestingFeedback', methods=['GET'])
def get_testing_feedback():
    token = extract_token(request)
    user_id = verify_and_get_id(token)
    course = int(request.args.get('Course'))
    assignment = int(request.args.get('Assignment'))
    group_id = int(request.args.get('Group'))

    if (user_handler.check_admin_or_course_teacher(user_id, course)):
        feedback = course_handler.get_assignment_feedback(course, assignment,
                                                          group_id)
        return make_response(jsonify(feedback), 200)

    else:
        return make_response({"status": 'not_teacher_in_course'}, 401)


@app.route('/getGroups', methods=['GET'])
def get_course_groups():
    token = extract_token(request)
    user_id = verify_and_get_id(token)
    course = int(request.args.get('Course'))

    if (user_id):
        if (user_handler.is_in_course(user_id, course)):
            groups = course_handler.get_course_groups(course)
            return make_response(jsonify(groups), 200)
        else:
            return make_response("not_in_course", 401)
    else:
        return make_response("not_logged_in", 401)


@app.route('/getGroup', methods=['GET'])
def get_course_group():
    token = extract_token(request)
    user_id = verify_and_get_id(token)
    course = int(request.args.get('Course'))
    group_id = int(request.args.get('GroupId'))

    if (user_id):
        if (user_handler.is_in_course(user_id, course)):
            group = course_handler.get_course_group(course, group_id)
            return make_response(jsonify(group), 200)
        else:
            return make_response("not_in_course", 401)
    else:
        return make_response("not_logged_in", 401)


@app.route('/assignmentsOverview', methods=['GET'])
def get_overview():
    token = extract_token(request)
    user_id = verify_and_get_id(token)
    course = int(request.args.get('Course'))

    if (user_handler.check_admin_or_course_teacher(user_id, course)):
        # create overview
        overview = course_handler.get_assignment_overview(course)
        return make_response(jsonify(overview), 200)
    else:
        return make_response(jsonify({"status": "no_permission"}), 401)


@app.route('/setFeedback', methods=['POST'])
def set_feedback():
    token = extract_token(request)
    user_id = verify_and_get_id(token)
    data = request.get_json()
    course: int = int(data['Course'])
    assignment: int = int(data['Assignment'])
    submission: int = int(data['Submission'])
    feedback: str = str(data['Feedback'])
    grade: bool = bool(data['Grade'])
    group_id: int = int(data['Group'])
    score: int = int(data['Score'])

    if (user_handler.check_admin_or_course_teacher(user_id, course)):
        course_handler.set_teacher_feedback(group_id, feedback, grade, course,
                                            assignment, submission, user_id,
                                            score)
        return make_response("", 200)
    else:
        return make_response(jsonify({"status": "no_permission"}), 401)


@app.route('/getTestFileNames', methods=['GET'])
def get_test_file_names():
    token = extract_token(request)
    user_id = verify_and_get_id(token)
    course = int(request.args.get('Course'))
    assignment = int(request.args.get('Assignment'))

    if (user_handler.check_admin_or_course_teacher(user_id, course)):
        # create overview
        overview = get_test_filenames(course, assignment)
        return make_response(jsonify(overview), 200)
    else:
        return make_response(jsonify({"status": "no_permission"}), 401)


@app.route('/getFilenames', methods=['GET'])
def get_file_names():
    token = extract_token(request)
    user_id = verify_and_get_id(token)
    course = int(request.args.get('Course'))
    assignment = int(request.args.get('Assignment'))

    if (user_handler.is_in_course(user_id, course)):
        # create overview
        filenames = get_filenames(course, assignment)
        return make_response(jsonify({'Filenames': filenames}), 200)
    else:
        return make_response(jsonify({"status": "no_permission"}), 401)


@app.route('/getCourseProgress', methods=['GET'])
def get_progress():
    token = extract_token(request)
    user_id = verify_and_get_id(token)

    if (user_handler.is_in_course):
        prog = course_handler.get_progress(user_id)
        return make_response(jsonify(prog), 200)
    else:
        return make_response("", 401)


@app.route('/changeCourseName', methods=['POST'])
def change_course_name():
    token = extract_token(request)
    user_id = verify_and_get_id(token)
    data = request.get_json()
    new_name = data['Name']
    course = int(data['Course'])

    if (user_id):
        if (user_handler.check_admin_or_course_teacher(user_id, course)):
            course_handler.change_course_name(new_name, course)
            return make_response("", 200)
        else:
            return make_response(jsonify({'status': 'Not a course teacher'}),
                                 401)
    else:
        return make_response(jsonify({'status': 'no_permission'}), 401)
