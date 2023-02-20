from flask import Flask, jsonify, request
from flask_cors import CORS

from .file_handler import handle_files, handle_testFile

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
    res = handle_testFile(files)
    return jsonify(res[0]), res[1]


    
    



