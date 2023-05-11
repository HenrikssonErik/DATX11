import subprocess
import pathlib
from .user_handler import Role


def check_against_ldap(cid: str) -> tuple[str, str] | None:
    output = subprocess.run(
        ['go', 'run', 'cidCheck.go', cid],
        capture_output=True,
        cwd=pathlib.Path(__file__).absolute().parent
    )

    # convert bytes to string and remove whitespace
    result = output.stdout.decode().strip()

    b_student = "student" in result.lower()
    b_employee = "employee" in result.lower()
    b_ta = "amanuens" in result.lower()
    b_phd = "doktorand" in result.lower()
    b_intern = "praktikant" in result.lower()
    b_no_title = result.count(':')
    name = result.split(",")[0]

    if (b_ta or b_phd or b_student or b_no_title or b_intern):
        return Role.Student.name, name
    elif (b_employee):
        return Role.Teacher.name, name
    else:
        # Default to student, could only have the else statement
        # but this will make future changes 'easier'
        return Role.Student.name, name
