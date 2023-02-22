from flask import Flask, jsonify, request, send_file
from flask_cors import CORS

from .file_handler import handle_files, handle_test_file, get_assignment_file_from_database

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
def post_files():
    data = get_assignment_file_from_database(1,5,1, 'Test1.pdf')
    return send_file(data, as_attachment=True, download_name='Test1.pdf')


