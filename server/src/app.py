from io import BytesIO
import os
import time
from typing import BinaryIO
from flask import Flask, Response, after_this_request, jsonify, make_response, request, send_file
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

#should be a post further on
@app.route('/getAssignmentFile', methods=['POST'])
def get_files():
    data = request.get_json()
    groupId = data['groupId']
    course = data['course']
    assignment = data['assignment']
    filename = data['filename'] ## should also be imported from frontend
    result = get_assignment_files_from_database(groupId,course,assignment, filename) #here we should send in info from user
    
    res= make_response(send_file(path_or_file= result, download_name=filename, as_attachment=True))

    headers= {"Access-Control-Expose-Headers": "Content-Disposition", 'Content-Disposition': 'attachment; filename={}'.format(filename)}
    res.headers= headers
    return res

    
