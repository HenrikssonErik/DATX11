import os


def get_conn_string() -> str:
    file_path = os.path.join(
        os.path.dirname(
            os.path.abspath(
                __file__)),
        'connection.txt')
    with open(file_path, 'r') as file:
        conn_lines = file.readlines()
        conn_str = "host=" + conn_lines[0] + \
            "port=" + conn_lines[1] + \
            "dbname=" + conn_lines[2] + \
            "user=" + conn_lines[3] + \
            "password=" + conn_lines[4]
    return conn_str
