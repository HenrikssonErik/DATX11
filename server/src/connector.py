from pathlib import Path


def get_conn_string() -> str:
    file_path = Path(__file__).absolute().parent / "connection_config.txt"
    with open(file_path, 'r') as file:
        conn_str = file.readline()
    return conn_str
