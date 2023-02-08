from flask import Flask, jsonify, request, make_response
from flask_cors import CORS
#could be used to sanitize file names but TAs will decide allowed filenamnes so it is probably not needed

from .fileHandler import handle_files

# creating the Flask application
app = Flask(__name__)

#made need to change
CORS(app)

#useless in the future, TODO: Remove along with front end button
@app.route('/test', methods=['GET'])
def testGet(): 
    #do the doings here
    return jsonify("hello")

@app.route('/files', methods=['POST'])
def post_files(): 
    
    files = request.files.getlist('files')

    if not files:
        return "Files not found", 406

    return handle_files(files)