import os


def get_conn_string() -> str:
    file_path = os.path.join(
        os.path.dirname(
            os.path.abspath(
                __file__)),
        'connection_config.txt')
    with open(file_path, 'r') as file:
        conn_str = file.readline()
        print(conn_str)
    return conn_str
