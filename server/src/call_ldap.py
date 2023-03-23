import subprocess
import pathlib

def check_against_ldap(cid: str):
    output = subprocess.run(['go', 'run', 'cidCheck.go', cid], capture_output=True, cwd=pathlib.Path(__file__).absolute().parent)
    result = output.stdout.decode().strip()  # convert bytes to string and remove whitespace

    b_student = "student" in result.lower()
    b_teacher = "employee" in result.lower()
    b_ta = "amanuens" in result.lower()
    name = result.split(",")[0]

    if (b_teacher and not b_ta):
        return ["Teacher", name ]
    if (b_student):
        return ["Student", name] 
    else:
        return ["false", "false"]