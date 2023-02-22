from werkzeug.utils import secure_filename
from werkzeug.datastructures import FileStorage
from . import general_tests
import tempfile
from pathlib import Path

__ALLOWED_EXTENSIONS = {'txt', 'pdf', 'py'}
# TODO: temp variables, should be taken from database when it is implemented
__allowed_filenames = {"Test1.pdf", "test2.txt", "test_runner.py"}
__nr_of_files = 1


def handle_files(files: list[FileStorage]) -> tuple[dict[str, str], int]:
    """
    Sanitizes files, checks for number of files, allowed file names and file
    types

    Returns: json object with feedback on submitted files
    """

    response_args = {}
    res_code = 200

    
    file_msg, res_code = ("OK", res_code) if (len(files) == __nr_of_files) else (f"Received {len(files)}, " + f"should be {__nr_of_files} files", 406)

    response_args.update({"number_of_files": file_msg})

    #Could do the same one-line if-else as above instead of one after the other in this for-loop
    for file in files:
        res_object = {}
        file.filename = secure_filename(file.filename)
        print(file.filename)
        res_object.update({"file": file.filename})

        file_name, res_code = ("OK", res_code) if (file.filename in __allowed_filenames) else ("Not allowed file name", 406)
        res_object.update({"file_name": file_name})

        file_type, res_code = ("OK", res_code) if (allowed_file(file.filename)) else ("Not allowed file type", 406)
        res_object.update({"file_type": file_type})

        response_args.update({"tested_file": res_object})

    # TODO: decide what to do with the files here, eg.
    # file.save(file.filename), to save the file to dir

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


# Method to check file extension for allowed files
def allowed_file(filename: str):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in __ALLOWED_EXTENSIONS

def saveToDB(file: FileStorage, groupId, course):
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
    conn = psycopg2.connect(host="95.80.39.50", port="5432", dbname="test_erp", user="postgres", password="BorasSuger-1")

    filetype = file.filename.rsplit('.', 1)[1].lower();    
    with conn.cursor() as cur:
        query = """INSERT INTO
    AssignmentFiles (GroupId, course, filename, filedata, filetype)
    VALUES (%s, %s, %s, %s, %s);"""

        
        cur.execute(query, (groupId, course, file.filename, binary, filetype))
        conn.commit()

def resubmit_files(file: FileStorage, groupId, course):
    print("Resubmission")
    
    conn = psycopg2.connect(host="95.80.39.50", port="5432", dbname="test_erp", user="postgres", password="BorasSuger-1")
    cursor = conn.cursor()

    queryData = "DELETE FROM AssignmentFiles WHERE assignmentfiles.filename = %s AND assignmentfiles.groupid = %s AND assignmentfiles.course = %s"
    cursor.execute(queryData, (file.filename, groupId, course))

    saveToDB(file, groupId, course)



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
