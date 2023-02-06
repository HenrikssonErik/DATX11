from flask import Flask, jsonify, request, make_response
from flask_cors import CORS
#could be used to sanitize file names but TAs will decide allowed filenamnes so it is probably not needed
from werkzeug.utils import secure_filename

# creating the Flask application
app = Flask(__name__)
CORS(app)

ALLOWED_EXTENSIONS = {'txt', 'pdf', 'py'}

#temp variables, should be moved to another package later
allowed_filenames = {"test", "test2"}
nr_of_files = 3

@app.route('/test', methods=['GET'])
def testGet(): 
    #do the doings here
    return jsonify("hello")

@app.route('/files', methods=['POST'])
def post_files(): 
    #do the doings here
    print('recieved request')
    files = request.files.getlist('files')

    if not files:
        return "Files not found", 406

    response_args = {}
    res_code = 200

    #check number of files
    if not(len(files) == nr_of_files):
        response_args.update({"Wrong amount of files": "Recieved " + str(len(files)) + ", should be " + str(nr_of_files) + " files"})
    
    for file in files:
        res_object = {}

        #add check duplicate files
        if not (file.filename in allowed_filenames):
            res_object.update({"File Name": "Not allowed file name"})
            res_code = 406
        else: 
            res_object.update({"Name": "OK!"})

        if not (allowed_file(file.filename)): 
            res_object.update({"File Type": " Not allowed filetype"})
            res_code = 406
        else:
            res_object.update({"File Type": "OK!"})

        #file.save(file.filename), choose what to do with the files
        response_args.update({file.filename: res_object})
    print(response_args)
    return jsonify(response_args) , res_code

#checks file extension for allowed files
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS