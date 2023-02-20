from werkzeug.utils import secure_filename
from werkzeug.datastructures import FileStorage
from . import general_tests
import tempfile
from pathlib import Path
import os
import psycopg2

__ALLOWED_EXTENSIONS = {'txt', 'pdf', 'py'}
# TODO: temp variables, should be taken from database when it is implemented
__allowed_filenames = {"Test1.pdf", "test2.txt", "good.py"}
__nr_of_files = 1

#for DB, should be recieved from frontend(?) later on
courseId = 5
assignment=1
groupId= 1


def handle_files(files: list[FileStorage]) -> tuple[dict[str, str], int]:
    """
    Sanitizes files, checks for number of files, allowed file names and file
    types

    Returns: json object with feedback on submitted files
    """

    response_args = {}
    res_code = 200

    if not (len(files) == __nr_of_files):
        response_args.update(
            {
                "Wrong amount of files": f"Recieved {len(files)}, " +
                                         f"should be {__nr_of_files} files"
            }
        )
        res_code = 406

    for file in files:
        res_object = {}
        file.filename = secure_filename(file.filename)
        if not (file.filename in __allowed_filenames):
            res_object.update({"File Name": "Not allowed file name"})
            res_code = 406
        else:
            res_object.update({"File Name": "OK!"})

        if not (allowed_file(file.filename)):
            res_object.update({"File Type": " Not allowed filetype"})
            res_code = 406
        else:
            res_object.update({"File Type": "OK!"})

        response_args.update({file.filename: res_object})

    # if the files ar ok proceed to save and test them
    if (res_code == 200):
        for file in files:
            saveAssignmentToDB(file,groupId,courseId,assignment)

    # Running general tests here
        with tempfile.TemporaryDirectory(prefix="DATX11__") as dir:

            # saves the user submitted files in a temp dir
            dir_path = Path(dir)
            py_file_names = []
            for file in files:
                if file.filename is not None and file.filename.endswith(".py"):
                    py_file_names.append("./" + file.filename)
                    with open(dir_path / file.filename, "wb") as f:
                        f.write(file.stream.read())

            # Check PEP8 conventions + cyclomatic complexity
            pep8_result = general_tests.pep8_check(dir_path,
                                               filename_patterns=py_file_names
                                               )
            response_args.update({"PEP8_results": pep8_result})

    

    return response_args, res_code


def handle_testFile (files: FileStorage):
    response_args = {}
    res_code = 200

    for file in files:
        res_object = {}
        file.filename = secure_filename(file.filename)
        print(file.filename)
        
        if not (allowed_file(file.filename)):
            res_object.update({"File Type": " Not allowed filetype"})
            res_code = 406
        else:
            res_object.update({"File Type": "OK!"})

        response_args.update({file.filename: res_object})
    
    #add renamin the files
        saveTestToDB(file)


    return response_args, res_code


# Method to check file extension for allowed files
def allowed_file(filename: str):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in __ALLOWED_EXTENSIONS


def saveTestToDB(file: FileStorage):
    print("saving to Db")
    print(file)

    if(os.path.exists(file.filename)):
        ##this is very dangerous, e.g if the submitted file is "app.py" wveryhting breaks!! TODO: change this
        print("file exists")
        os.remove(file.filename)
        print("file removed, new file is being saved.")
    file.save(file.filename)
    f= open(file.filename,"rb") #rb = reading in binary
    filedata = f.read()
    print("read file")
    print(filedata)
    binary = psycopg2.Binary(filedata)
    
    #the DB-login data should not be shown here, better to load it from local document
    conn = psycopg2.connect(host="95.80.39.50", port="5432", dbname="hydrant", user="postgres", password="BorasSuger-1")

    with conn.cursor() as cur:
        query = """INSERT INTO
    TestFiles (courseId, assignment, filename, filedata)
    VALUES (%s, %s, %s,%s);"""

        
        cur.execute(query, (courseId, assignment, file.filename, binary))
        conn.commit()

def saveAssignmentToDB(file: FileStorage, groupId, courseId, assignment):
    print("saving to Db")
    print(file)

    if(os.path.exists(file.filename)):
        print("file exists")
        os.remove(file.filename)
        print("file removed, new file is being saved.")
    file.save(file.filename)
    f= open(file.filename,"rb") #rb = reading in binary
    filedata = f.read()
    print("read file")
    print(filedata)
    binary = psycopg2.Binary(filedata)
    
    #the DB-login data should not be shown here, better to load it from local document
    conn = psycopg2.connect(host="95.80.39.50", port="5432", dbname="hydrant", user="postgres", password="BorasSuger-1")

    filetype = file.filename.rsplit('.', 1)[1].lower();    
    with conn.cursor() as cur:
        query = """INSERT INTO
    AssignmentFiles (GroupId, CourseId, Assignment, filename, filedata, filetype)
    VALUES (%s, %s, %s, %s, %s, %s);"""

        
        cur.execute(query, (groupId, courseId, assignment, file.filename, binary, filetype))
        conn.commit()

def resubmit_files(file: FileStorage, groupId, course):
    print("Resubmission")
    
    conn = psycopg2.connect(host="95.80.39.50", port="5432", dbname="hydrant", user="postgres", password="BorasSuger-1")
    cursor = conn.cursor()

    queryData = "DELETE FROM AssignmentFiles WHERE assignmentfiles.filename = %s AND assignmentfiles.groupid = %s AND assignmentfiles.courseid = %s"
    cursor.execute(queryData, (file.filename, groupId, course))

    saveAssignmentToDB(file, groupId, course)



def get_file_from_database(groupId, course, fileName):
    print("Retrieving from database")

    conn = psycopg2.connect(host="95.80.39.50", port="5432", dbname="test_erp", user="postgres", password="BorasSuger-1")
    cursor = conn.cursor()
    queryData = "SELECT FileData FROM AssignmentFiles WHERE assignmentfiles.filename = %s AND assignmentfiles.groupid = %s AND assignmentfiles.course = %s"
    cursor.execute(queryData, (fileName, groupId, course))
    data = cursor.fetchall()
    file_binary = data[0][0].tobytes()
    with open(fileName,'wb') as file: #wb = write in binary
        file.write((file_binary))
