from werkzeug.utils import secure_filename
from werkzeug.datastructures import FileStorage
from . import general_tests
import tempfile
from pathlib import Path
import os
import psycopg2

__ALLOWED_EXTENSIONS = {'txt', 'pdf', 'py'}
# TODO: temp variables, should be taken from database when it is implemented
__allowed_filenames = {"Test1.pdf", "test2.txt", "PythonFile.py"}
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
        with tempfile.TemporaryDirectory(prefix="DATX11__") as dir:
            save_dir = Path(dir)/"saves"
            save_dir.mkdir()
            file_paths: list[Path] = []

            # save file to tempdir
            for file in files:
                if file.filename is None:
                    raise ValueError("filename does not exits")

                with open(save_dir/file.filename, "wb") as f:
                    f.write(file.stream.read())
                    file_paths.append(save_dir/file.filename)

            # read the filename and filedata from `save_dir` and give it to
            # saveAssignmentToDB
            for file_path in file_paths:
                filename = file_path.name
                filedata = file_path.read_bytes()

                save_assignment_to_db(filename, filedata,
                                   groupId, courseId, assignment)

        # Running general tests here

            # saves the user submitted files in a temp dir
            pep8_test_dir = Path(dir)/"pep8_tests"
            pep8_test_dir.mkdir()
            py_file_names = []
            for file_path in file_paths:
                if file_path.suffix == ".py":
                    f_name = pep8_test_dir/file_path.name
                    py_file_names.append("./" + str(file_path.name))
                    f_name.write_bytes(file_path.read_bytes())

            # Check PEP8 conventions + cyclomatic complexity
            pep8_result = general_tests.pep8_check(
                pep8_test_dir,
                filename_patterns=py_file_names
            )

            response_args.update({"PEP8_results": pep8_result})

    return response_args, res_code


def handle_test_file (files: FileStorage):
    response_args = {}
    res_code = 200

    for file in files:
        res_object = {}
        file.filename = secure_filename(file.filename)
        
        if not (allowed_file(file.filename)):
            res_object.update({"File Type": " Not allowed filetype"})
            res_code = 406
        else:
            res_object.update({"File Type": "OK!"})

        response_args.update({file.filename: res_object})
    
        save_test_to_db(file,courseId, assignment)


    return response_args, res_code


# Method to check file extension for allowed files
def allowed_file(filename: str):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in __ALLOWED_EXTENSIONS


def save_test_to_db(file: FileStorage, courseId, assignment):

    file.filename = str(courseId) + 'Tests' + str(assignment)+'.py'

    if(os.path.exists(file.filename)): 
        raise Exception("file exists in dir, not allowed filename")
        
    file.save(file.filename)
    f= open(file.filename,"rb") #rb = reading in binary
    filedata = f.read()
    binary = psycopg2.Binary(filedata)
    
    #the DB-login data should not be shown here, better to load it from local document
    conn = psycopg2.connect(host="95.80.39.50", port="5432", dbname="hydrant", user="postgres", password="BorasSuger-1")

    with conn.cursor() as cur:
        query = """INSERT INTO
    TestFiles (courseId, assignment, filename, filedata)
    VALUES (%s, %s, %s,%s);"""

        
        cur.execute(query, (courseId, assignment, file.filename, binary))
        conn.commit()

    f.close()
    os.remove(file.filename)

def save_assignment_to_db(filename: str, filedata: bytes, groupId, courseId, assignment):
    """ Saves assignmentfile to the database and removed previous file if it exists """
    #if it is a resubmission a remove is done before adding the new file
    remove_existing_assignment(filename, groupId,courseId,assignment )
    binary = psycopg2.Binary(filedata)

    # the DB-login data should not be shown here, better to load it from local document
    conn = psycopg2.connect(host="95.80.39.50", port="5432",
                            dbname="hydrant", user="postgres", password="BorasSuger-1")

    filetype = filename.rsplit('.', 1)[1].lower()
    with conn.cursor() as cur:
        query = """INSERT INTO
    AssignmentFiles (GroupId, CourseId, Assignment, filename, filedata, filetype)
    VALUES (%s, %s, %s, %s, %s, %s);"""

        cur.execute(query, (groupId, courseId, assignment,
                    filename, binary, filetype))
        conn.commit()

def remove_existing_assignment(filename: str, groupId, course, assignment):
    """ Removes file from assignment table in the database"""
    conn = psycopg2.connect(host="95.80.39.50", port="5432", dbname="hydrant", user="postgres", password="BorasSuger-1")
    cursor = conn.cursor()

    queryData = """DELETE FROM AssignmentFiles WHERE assignmentfiles.filename = %s AND assignmentfiles.groupid = %s AND assignmentfiles.courseid = %s AND assignmentfiles.assignment = %s;"""
    cursor.execute(queryData, (filename, groupId, course, assignment))
    conn.commit()
    #save_assignment_to_db(file, groupId, course)



def get_assignment_file_from_database(groupId, course, assignment, fileName):
    """retrieves file from database"""
    print("Retrieving from database")

    conn = psycopg2.connect(host="95.80.39.50", port="5432", dbname="test_erp", user="postgres", password="BorasSuger-1")
    cursor = conn.cursor()
    queryData = "SELECT FileData FROM AssignmentFiles WHERE assignmentfiles.filename = %s AND assignmentfiles.groupid = %s AND assignmentfiles.courseid = %s AND assignmentfiles.assignment = %s"
    cursor.execute(queryData, (fileName, groupId, course, assignment))
    data = cursor.fetchall()
    file_binary = data[0][0].tobytes()
    with open(fileName,'wb') as file: #wb = write in binary
        file.write((file_binary))
