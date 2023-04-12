import io
from pathlib import Path
import tempfile
from . import general_tests
import psycopg2
from werkzeug.utils import secure_filename
from werkzeug.datastructures import FileStorage
from .connector import get_conn_string


__ALLOWED_EXTENSIONS = {'txt', 'pdf', 'py'}


def handle_files(files: list[FileStorage], course: int, group: int,
                 assignment: int) -> tuple[list[dict[str, str]],
                                           dict[str, str], int]:
    """Sanitizes files, checks for number of files,
    allowed file names and file types
    Returns: json object with feedback on submitted files
    """

    __allowed_filenames: tuple = get_filenames(course, assignment)
    __nr_of_files = len(__allowed_filenames)
    print(__allowed_filenames)
    print(__nr_of_files)

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
        save_to_temp_and_database(files, response_items, group, course, assignment)

    return response_items, number_of_files, res_code


def get_filenames(course: int, assignment: int) -> tuple:
    conn = psycopg2.connect(dsn=get_conn_string())
    try:
        with conn:
            with conn.cursor() as cur:
                query = """SELECT filename FROM filenames
                        WHERE filenames.courseId   = %s
                        AND filenames.assignment = %s
                        """

                cur.execute(query, (course, assignment))
                data = cur.fetchall()
        conn.close()
        return tuple(value[0] for value in data)

    except Exception as e:
        print(e)
        return ()


def save_to_temp_and_database(
        files: list[FileStorage],
        response_items: dict,
        group_id: int,
        course_id: int,
        assignment: int
) -> None:
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

            save_assignment_to_db(
                file_name, file_data, group_id, course_id, assignment
            )
        pep8_test_dir = Path(dir)/"pep8_tests"
        pep8_test_dir.mkdir()

        for count, file_path in enumerate(file_paths):
            pep8_result = "OK"
            if file_path.suffix == ".py":
                f_name = pep8_test_dir/file_path.name
                f_name.write_bytes(file_path.read_bytes())

                pep8_result = general_tests.pep8_check(
                    pep8_test_dir,
                    filename_patterns=["./" + str(file_path.name)]
                )

            response_items[count].update({"PEP8_results": pep8_result})


def handle_test_file(files: list[FileStorage], course_id: int,
                     assignment: int) -> tuple[dict, int]:
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


def allowed_file(filename: str) -> bool:
    """Retrieve extension from full file name"""

    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in __ALLOWED_EXTENSIONS


def save_test_to_db(file: FileStorage, course_id: int, assignment: int):
    """Saves the teacher's tests to the database"""

    file.filename = file.filename + 'TestFile.py'
    remove_existing_test_file(file.filename, course_id, assignment)
    binary = psycopg2.Binary(file.stream.read())

    conn = psycopg2.connect(dsn=get_conn_string())

    with conn:
        with conn.cursor() as cur:
            query = """INSERT INTO TestFiles
                    (courseId, assignment, filename, filedata)
                    VALUES (%s, %s, %s,%s);
                    """

            cur.execute(query, (course_id, assignment, file.filename, binary))
    conn.close()


def remove_existing_assignment(file_name: str, group_id: int, course_id: int,
                               assignment: int, submission: int):
    """Outdated and not needed anymore"""

    conn = psycopg2.connect(dsn=get_conn_string())

    with conn:
        with conn.cursor() as cur:
            query = """DELETE FROM AssignmentFiles
                 WHERE assignmentFiles.fileName   = %s
                 AND   assignmentFiles.groupId    = %s
                 AND   assignmentFiles.courseId   = %s
                 AND   AssignmentFiles.assignment = %s
                 AND   AssignmentFiles.submission = %s;
                 """

            cur.execute(query, (file_name, group_id, course_id, assignment, submission))
    conn.close()


def save_assignment_to_db(file_name: str, file_data: bytes, group_id: int,
                          course_id: int, assignment: int):
    """Saves assignmentfile to the database

    Removed previous file if it exists
    """
    # We do not need to delete an assignment with several submission anymore. 
    # remove_existing_assignment(file_name, group_id, course_id, assignment)
    binary = psycopg2.Binary(file_data)

    conn = psycopg2.connect(dsn=get_conn_string())

    file_type = file_name.rsplit('.', 1)[1].lower()
    with conn:
        with conn.cursor() as cur:
            query = """INSERT INTO AssignmentFiles
                    (groupId, courseId, assignment, fileName,
                    fileData, fileType) 
                    VALUES (%s, %s, %s, %s, %s, %s);
                    """

            cur.execute(query, (group_id, course_id, assignment,
                        file_name, binary, file_type))
    conn.close()


def remove_existing_test_file(
        file_name: str,
        course_id: int,
        assignment: int
):
    """Removes file from testFile table in the database"""

    conn = psycopg2.connect(dsn=get_conn_string())
    with conn:
        with conn.cursor() as cur:
            query_data = """DELETE FROM TestFiles
                 WHERE testfiles.filename   = %s
                 AND   testfiles.courseid   = %s
                 AND   testfiles.assignment = %s;
                 """
            cur.execute(query_data, (file_name, course_id, assignment))
    conn.close()


def get_assignment_files_from_database(
        group_id: int,
        course: int,
        assignment: int,
        file_name: str,
        submission: int
):
    """Retrieves file from database"""

    conn = psycopg2.connect(dsn=get_conn_string())
    with conn:
        with conn.cursor() as cur:
            query_data = """SELECT FileData FROM AssignmentFiles
                        WHERE AssignmentFiles.fileName   = %s
                        AND   AssignmentFiles.groupId    = %s
                        AND   AssignmentFiles.courseId   = %s
                        AND   AssignmentFiles.assignment = %s
                        AND   AssignmentFiles.submission = %s
                        """

            cur.execute(query_data, (file_name, group_id, course, assignment, submission))
            data = cur.fetchall()
    conn.close()

    file_binary = io.BytesIO(data[0][0].tobytes())
    return file_binary
