
from flask import Flask, jsonify, request, make_response
from flask_cors import CORS

# creating the Flask application
app = Flask(__name__)
CORS(app)


@app.route('/test', methods=['GET'])
def testGet(): 
    #do the doings here
    return jsonify("hello")

@app.route('/files', methods=['POST'])
def testPOST(): 
    #do the doings here
    print('recieved request')
    files = request.files.getlist('files')

    if not files:
        return "No file man"
        
    for file in files:
        print('in loop')
        print(file.filename)
        file.save(file.filename)
   # print(file)
    return 'success' , 200

