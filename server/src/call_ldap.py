import subprocess
import pathlib

def check_against_ldap(cid: str):
    print(cid)
    output = subprocess.run(['go', 'run', 'cidCheck.go', cid], capture_output=True, cwd=pathlib.Path(__file__).absolute().parent)
    print("Output: ", output)
    result = output.stdout.decode().strip()  # convert bytes to string and remove whitespace
    print(result)
    return result == "User Exists"

