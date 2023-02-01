
from flask import Flask, jsonify, request, make_response
from flask_cors import CORS

# creating the Flask application
app = Flask(__name__)
CORS(app)


@app.route('/test', methods=['GET'])
def testGet(): 
    #do the doings here
    return jsonify("hello")

