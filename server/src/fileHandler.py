

from flask import jsonify
from werkzeug.utils import secure_filename

#TODO: temp variables, should be taken from database when it is implemented
__ALLOWED_EXTENSIONS = {'txt', 'pdf', 'py'}
__allowed_filenames = {"test1.pdf", "test2.txt", "fileHandlerTest.py"}
__nr_of_files = 1

"""
Sanitizes files, checks for number of files, allowed file names and file types
Returns: json object with feedback on submitted files
"""
def handle_files(files): 

    response_args = {}
    res_code = 200

    if not(len(files) == __nr_of_files):
        response_args.update({"Wrong amount of files": "Recieved " + str(len(files)) + ", should be " + str(__nr_of_files) + " files"})
    
    for file in files:
        res_object = {}

        file.filename = secure_filename(file.filename)
        
        if not (file.filename in __allowed_filenames):
            res_object.update({"File Name": "Not allowed file name"})
            res_code = 406
        else: 
            res_object.update({"Name": "OK!"})

        if not (allowed_file(file.filename)): 
            res_object.update({"File Type": " Not allowed filetype"})
            res_code = 406
        else:
            res_object.update({"File Type": "OK!"})

        
        response_args.update({file.filename: res_object})

        #TODO: decide what to do with the files here, eg. file.save(file.filename), to save the file
    return jsonify(response_args) , res_code
    
#Method to check file extension for allowed files
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in __ALLOWED_EXTENSIONS