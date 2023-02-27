
from flask import Flask, jsonify, make_response, request, send_file
from flask_cors import CORS
from .file_handler import handle_files, \
    handle_test_file, get_assignment_files_from_database

# creating the Flask application
app = Flask(__name__)

CORS(app)


# useless in the future, TODO: Remove along with front end button
@app.route('/test', methods=['GET'])
def test_get():
    return jsonify("hello")


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
    groupId = data['groupId']
    course = data['course']
    assignment = data['assignment']
    filename = data['filename']  # should also be imported from frontend
    result = get_assignment_files_from_database(groupId, course, assignment, filename)

    res = make_response(send_file(path_or_file=result,
                                   download_name=filename, as_attachment=True))

    headers = {"Access-Control-Expose-Headers": "Content-Disposition", 'Content-Disposition': 'attachment; filename={}'.format(filename)}
    res.headers = headers
    return res
