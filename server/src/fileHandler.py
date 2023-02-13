

from werkzeug.utils import secure_filename
from werkzeug.datastructures import FileStorage
import psycopg2

__ALLOWED_EXTENSIONS = {'txt', 'pdf', 'py'}
#TODO: temp variables, should be taken from database when it is implemented
__allowed_filenames = {"Test1.pdf", "test2.txt", "PythonFile.py"}
__nr_of_files = 1



def handle_files(files:list[FileStorage]) -> tuple[dict[str, str], int] : 
    """
    Sanitizes files, checks for number of files, allowed file names and file types
    Returns: json object with feedback on submitted files
    """

    response_args = {}
    res_code = 200

    if not(len(files) == __nr_of_files):
        response_args.update({"Wrong amount of files": "Recieved " + str(len(files)) + ", should be " + str(__nr_of_files) + " files"})
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
        saveToDB(file)
    #TODO: decide what to do with the files here, eg. file.save(file.filename), to save the file to dir
    return response_args , res_code
    
#Method to check file extension for allowed files
def allowed_file(filename: str):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in __ALLOWED_EXTENSIONS

def saveToDB(file: FileStorage):
    print("saving to Db")
    print(file)
    file.save(file.filename)
    f= open(file.filename,"rb") #rb = reading in binary
    filedata = f.read()
    print("read file")
    print(filedata)
    binary = psycopg2.Binary(filedata)
    conn = psycopg2.connect(host="95.80.39.50", port="5432", dbname="test_erp", user="postgres", password="BorasSuger-1")

    with conn.cursor() as cur:
        query = """INSERT INTO
    AssignmentFiles (GroupId, course, filename, filedata, filetype)
    VALUES (%s, %s, %s, %s, %s);"""

        cur.execute(query, (700,'tda357', file.filename, binary, 'pdf'))
        conn.commit()
        
