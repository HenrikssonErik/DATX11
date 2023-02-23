from flask import Flask, Response, jsonify, make_response, request, send_file
from flask_cors import CORS

from .file_handler import handle_files, handle_test_file, get_assignment_files_from_database

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

    return jsonify(res[0]), res[1]
    

@app.route('/unitTest', methods=['POST'])
def post_tests ():
    print(request)
    files = request.files.getlist('files')

    if not files:
        return "Files not found", 406
    res = handle_test_file(files)
    return jsonify(res[0]), res[1]

@app.route('/getAssignmentFiles', methods=['GET'])
def get_files():

    get_assignment_files_from_database(6,6,6, 'Test1.pdf')

    headers= {"Access-Control-Expose-Headers": "Content-Disposition", 'Content-Disposition': 'attachment; filename={}'.format("Test.pdf")}
    res = make_response(send_file(path_or_file=r"C:\Users\sebas\Documents\GitHub\DATX11\server\src\Test1.pdf"))
    res.headers= headers
    
    return res
