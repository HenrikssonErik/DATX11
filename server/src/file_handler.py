import io
import os
from pathlib import Path
import tempfile

from . import general_tests
import psycopg2
from werkzeug.utils import secure_filename
from werkzeug.datastructures import FileStorage


__ALLOWED_EXTENSIONS = {'txt', 'pdf', 'py'}
# TODO: temp variables, should be taken from database when it is implemented

__allowed_filenames = {"Test1.pdf", "test2.txt", 
                       "1ha1.py", "PythonFile.py"}
__nr_of_files = 1

# for DB, should be recieved from frontend(?) later on
course_id = 6
assignment = 6
group_id = 6

def handle_files(files: list[FileStorage]) -> tuple[list[dict[str, str]], 
                                                    dict[str, str], int]: 
    """Sanitizes files, checks for number of files, 
    allowed file names and file types
    Returns: json object with feedback on submitted files
    """
    number_of_files = {}
    res_code = 200
    file_amount, res_code = ("OK", res_code)  \
        if (len(files) == __nr_of_files) \
        else (f"Received {len(files)}, should be {__nr_of_files} files",
              406)

    number_of_files.update({"number_of_files": file_amount})
    response_items = []

    for file in files:
        res_object = {}
        file.filename = secure_filename(file.filename)
        res_object.update({"file": file.filename})

        file_name, res_code = ("OK", res_code) \
            if (file.filename in __allowed_filenames) \
            else ("Not allowed file name", 406)
        res_object.update({"file_name": file_name})
        file_type, res_code = ("OK", res_code) \
            if (allowed_file(file.filename)) \
            else ("Not allowed file type", 406)
        res_object.update({"file_type": file_type})

        response_items.append({"tested_file": res_object})

    if (res_code == 200):
        save_to_temp_and_database(files, response_items)

    return response_items, number_of_files, res_code


def save_to_temp_and_database(files: list[FileStorage], response_items):
    """Downloads the file to temp directory and then to saves into 
    
    the database. Also checks pep8 and cyclomatic complexity.
    """

    with tempfile.TemporaryDirectory(prefix="DATX11__") as dir:
        save_dir = Path(dir)/"saves"
        save_dir.mkdir()
        file_paths: list[Path] = []
            
        for file in files:   # save file to tempdir
            if file.filename is None:
                raise ValueError("filename does not exits")

            with open(save_dir/file.filename, "wb") as f:
                f.write(file.stream.read())
                file_paths.append(save_dir/file.filename)

        for file_path in file_paths:
            file_name = file_path.name
            file_data = file_path.read_bytes()

            save_assignment_to_db(file_name, file_data,
                                    group_id, course_id, assignment)

        pep8_test_dir = Path(dir)/"pep8_tests"
        pep8_test_dir.mkdir()
        py_file_names = []
        for count, file_path in enumerate(file_paths):
            pep8_result = "OK"
            if file_path.suffix == ".py":
                f_name = pep8_test_dir/file_path.name
                py_file_names.append("./" + str(file_path.name))
                f_name.write_bytes(file_path.read_bytes())
                                
                pep8_result = general_tests.pep8_check(pep8_test_dir,
                    filename_patterns=py_file_names)

            response_items[count].update({"PEP8_results": pep8_result})


def handle_test_file(files: list[FileStorage]):
    """Handles the incoming test files to check if the type is allowed"""
    response_args = {}
    res_code = 200

    for file in files:
        res_object = {}
        file.filename = secure_filename(file.filename)

        if not (allowed_file(file.filename)):
            res_object.update({"File Type": " Not an allowed filetype"})
            res_code = 406
        else:
            res_object.update({"File Type": "OK!"})

        response_args.update({file.filename: res_object})

        save_test_to_db(file, course_id, assignment)

    return response_args, res_code


def allowed_file(filename: str):
    """Retrieve extension from full file name"""

    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in __ALLOWED_EXTENSIONS


def save_test_to_db(file: FileStorage, course_id, assignment):
    """Saves the teacher's tests to the database"""

    file.filename = str(course_id) + 'Tests' + str(assignment)+'.py'

    if (os.path.exists(file.filename)):
        raise Exception("file exists in dir, not allowed filename")

    file.save(file.filename)
    f = open(file.filename, "rb")  # rb = reading in binary
    file_data = f.read()
    binary = psycopg2.Binary(file_data)

    conn = psycopg2.connect(host="95.80.39.50", port="5432", dbname="hydrant",
                            user="postgres", password="BorasSuger-1")

    filetype = file.filename.rsplit('.', 1)[1].lower()
    with conn.cursor() as cur:
        query = """INSERT INTO TestFiles 
                (courseId, assignment, filename, filedata)
                VALUES (%s, %s, %s,%s);
                """

    cur.execute(query, (group_id, course_id, file.filename, binary, filetype))

    conn.commit()
    conn.close()
    f.close()
    os.remove(file.filename)


def save_assignment_to_db(file_name: str, file_data: bytes, group_id,
                          course_id, assignment):
    """Saves assignmentfile to the database

    Removed previous file if it exists
    """

    remove_existing_assignment(file_name, group_id, course_id, assignment)
    binary = psycopg2.Binary(file_data)

    conn = psycopg2.connect(host="95.80.39.50", port="5432", dbname="hydrant",
                            user="postgres", password="BorasSuger-1")

    file_type = file_name.rsplit('.', 1)[1].lower()
    with conn.cursor() as cur:
        query = """INSERT INTO AssignmentFiles 
                (GroupId, CourseId, Assignment, filename, filedata, filetype)
                VALUES (%s, %s, %s, %s, %s, %s);
                """

        cur.execute(query, (group_id, course_id, assignment,
                    file_name, binary, file_type))
        conn.commit()
        conn.close


def remove_existing_assignment(file_name: str, group_id, 
                               course_id, assignment):
    """Removes file from assignment table in the database"""
  
    conn = psycopg2.connect(host="95.80.39.50", port="5432", dbname="hydrant",
                            user="postgres", password="BorasSuger-1")
    cursor = conn.cursor()

    query_data = """DELETE FROM AssignmentFiles 
                 WHERE assignmentfiles.filename   = %s 
                 AND   assignmentfiles.groupid    = %s 
                 AND   assignmentfiles.courseid   = %s 
                 AND   assignmentfiles.assignment = %s;
                 """
                    
    cursor.execute(query_data, (file_name, group_id, course_id, assignment))
    conn.commit()
    conn.close()


def get_assignment_files_from_database(group_id, course, 
                                       assignment, file_name):
    """Retrieves file from database"""

    conn = psycopg2.connect(host="95.80.39.50", port="5432", dbname="hydrant",
                            user="postgres", password="BorasSuger-1")

    cursor = conn.cursor()
    query_data = """SELECT FileData FROM AssignmentFiles 
                WHERE assignmentfiles.filename   = %s
                AND   assignmentfiles.groupid    = %s 
                AND   assignmentfiles.courseid   = %s 
                AND   assignmentfiles.assignment = %s
                """
    
    cursor.execute(query_data, (file_name, group_id, course, assignment))
    
    data = cursor.fetchall()
    file_binary = io.BytesIO(data[0][0].tobytes())
    
    return file_binary

