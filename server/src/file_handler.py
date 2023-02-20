from werkzeug.utils import secure_filename
from werkzeug.datastructures import FileStorage
from . import general_tests
import tempfile
from pathlib import Path

__ALLOWED_EXTENSIONS = {'txt', 'pdf', 'py'}
# TODO: temp variables, should be taken from database when it is implemented
__allowed_filenames = {"Test1.pdf", "test2.txt", "PythonFile.py"}
__nr_of_files = 1


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
