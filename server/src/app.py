from flask import Flask, Response, jsonify, make_response, request, send_file
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
    return jsonify(feedback_res), res[1]


@app.route('/unitTest', methods=['POST'])
def post_tests():
    print(request)
    files = request.files.getlist('files')

    if not files:
        return "Files not found", 406
    res = handle_test_file(files)
    return jsonify(res[0]), res[1]


@app.route('/getAssignmentFiles', methods=['GET'])
def get_files():

    # TODO send all files with correct filename from a temp_dir, then remove files from the temp_dir toreset it
    result = get_assignment_files_from_database(1, 5, 1, 'test2.txt')

    # setfilename dynamiclly
    headers = {"Access-Control-Expose-Headers": "Content-Disposition",
               'Content-Disposition': 'attachment; filename={}'.format("Test")}
    res = make_response(send_file(path_or_file=result))
    res.headers = headers
    # remove files after res is created
    return res
