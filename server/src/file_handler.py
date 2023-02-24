from werkzeug.utils import secure_filename
from werkzeug.datastructures import FileStorage
from . import general_tests
import tempfile
from pathlib import Path
import os
import psycopg2

__ALLOWED_EXTENSIONS = {'txt', 'pdf', 'py'}
# TODO: temp variables, should be taken from database when it is implemented
__allowed_filenames = {"Test1.pdf", "test2.txt", "1ha1.py", "1file_handler.py"}
__nr_of_files = 2

# for DB, should be recieved from frontend(?) later on
courseId = 6
assignment = 6
groupId = 6


def handle_files(files: list[FileStorage]) -> tuple[list[dict[str, str]], dict[str, str], int]:
    """
    Sanitizes files, checks for number of files, allowed file names and file
    types

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

    # Could do the same one-line if-else as above instead of one after the
    # other in this for-loop
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

            for file_path in file_paths:
                filename = file_path.name
                filedata = file_path.read_bytes()

                save_assignment_to_db(filename, filedata,
                                      groupId, courseId, assignment)

            pep8_test_dir = Path(dir)/"pep8_tests"
            pep8_test_dir.mkdir()
            py_file_names = []
            for count, file_path in enumerate(file_paths):
                pep8_result = "OK"
                if file_path.suffix == ".py":
                    f_name = pep8_test_dir/file_path.name
                    py_file_names.append("./" + str(file_path.name))
                    f_name.write_bytes(file_path.read_bytes())

                    # Check PEP8 conventions + cyclomatic complexity
                    pep8_result = general_tests.pep8_check(
                        pep8_test_dir,
                        filename_patterns=py_file_names
                    )
                response_items[count].update({"PEP8_results": pep8_result})

    return response_items, number_of_files, res_code


def handle_test_file(files: list[FileStorage]):
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

        save_test_to_db(file, courseId, assignment)

    return response_args, res_code


# Method to check file extension for allowed files
def allowed_file(filename: str):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in __ALLOWED_EXTENSIONS


def save_test_to_db(file: FileStorage, courseId, assignment):

    file.filename = str(courseId) + 'Tests' + str(assignment)+'.py'

    if (os.path.exists(file.filename)):
        raise Exception("file exists in dir, not allowed filename")

    file.save(file.filename)
    f = open(file.filename, "rb")  # rb = reading in binary
    filedata = f.read()
    binary = psycopg2.Binary(filedata)

    # the DB-login data should not be shown here
    # better to load it from local document
    conn = psycopg2.connect(host="95.80.39.50",
                            port="5432",
                            dbname="hydrant",
                            user="postgres",
                            password="BorasSuger-1")

    filetype = file.filename.rsplit('.', 1)[1].lower()
    with conn.cursor() as cur:
        query = """INSERT INTO
        TestFiles (courseId, assignment, filename, filedata)
        VALUES (%s, %s, %s,%s);"""

    cur.execute(query, (groupId, courseId, file.filename, binary, filetype))

    conn.commit()
    conn.close()
    f.close()
    os.remove(file.filename)


def save_assignment_to_db(filename: str,
                          filedata: bytes,
                          groupId,
                          courseId,
                          assignment):
    """
    Saves assignmentfile to the database
    Removed previous file if it exists
    """
    # if it is a resubmission a remove is done before adding the new file
    remove_existing_assignment(filename, groupId, courseId, assignment)
    binary = psycopg2.Binary(filedata)

    # the DB-login data should not be shown here
    # better to load it from local document
    conn = psycopg2.connect(host="95.80.39.50",
                            port="5432",
                            dbname="hydrant",
                            user="postgres",
                            password="BorasSuger-1")

    filetype = filename.rsplit('.', 1)[1].lower()
    with conn.cursor() as cur:
        query = """INSERT INTO
    AssignmentFiles (GroupId, CourseId, Assignment,
                     filename, filedata, filetype)
    VALUES (%s, %s, %s, %s, %s, %s);"""

        cur.execute(query, (groupId, courseId, assignment,
                    filename, binary, filetype))
        conn.commit()
        conn.close


def remove_existing_assignment(filename: str, groupId, course, assignment):
    """ Removes file from assignment table in the database"""
    conn = psycopg2.connect(host="95.80.39.50",
                            port="5432",
                            dbname="hydrant",
                            user="postgres",
                            password="BorasSuger-1")
    cursor = conn.cursor()

    queryData = """DELETE FROM AssignmentFiles WHERE assignmentfiles.filename = %s AND assignmentfiles.groupid = %s AND assignmentfiles.courseid = %s AND assignmentfiles.assignment = %s;"""
    cursor.execute(queryData, (filename, groupId, course, assignment))
    conn.commit()
    conn.close()
    # save_assignment_to_db(file, groupId, course)


def get_assignment_files_from_database(groupId, course, assignment, fileName):
    """retrieves file from database"""

    conn = psycopg2.connect(host="95.80.39.50",
                            port="5432",
                            dbname="hydrant",
                            user="postgres",
                            password="BorasSuger-1")

    cursor = conn.cursor()
    queryData = "SELECT FileData FROM AssignmentFiles WHERE assignmentfiles.filename = %s AND assignmentfiles.groupid = %s AND assignmentfiles.courseid = %s AND assignmentfiles.assignment = %s"
    cursor.execute(queryData, (fileName, groupId, course, assignment))
    
    data = cursor.fetchall()
    #print(data[0][0])
    file_binary = io.BytesIO(data[0][0].tobytes())
    
    save_path =  'temp_directory/' #filedialog.askopenfilename(initialfile = fileName)
 
    completeName = os.path.join(save_path, fileName)         

    #with open(completeName, "wb") as file1:
    #   file1.write((file_binary))

    #file1.close()

    #return completeName
    return file_binary
    #this line creates a zip archive to, havent figuered out how to recreate it in front en though
    #make_archive("archiveName", 'zip',"zip-all-Files-in-this-dir" )

