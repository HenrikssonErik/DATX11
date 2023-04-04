import subprocess
import pathlib
from .user_handler import Role

def check_against_ldap(cid: str):
    output = subprocess.run(
        ['go', 'run', 'cidCheck.go', cid],
        capture_output=True,
        cwd=pathlib.Path(__file__).absolute().parent
    )

    # convert bytes to string and remove whitespace
    result = output.stdout.decode().strip()

    b_student = "student" in result.lower()
    b_teacher = "employee" in result.lower()
    b_ta = "amanuens" in result.lower()
    name = result.split(",")[0]

    if (b_teacher and not b_ta):
        return [Role.Teacher, name]
    if (b_student):
        return [Role.Student, name]
    else:
        return ["false", "false"]
