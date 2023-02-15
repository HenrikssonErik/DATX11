from pathlib import Path
import subprocess
import sys
import errno
import os


def pep8_check(
    run_directory: Path,
    filename_patterns: list[str] | None = None,
    flake8_config: None | Path = None
) -> str:
    """Check different pep8 conventions in python files.

    Parameters
    ----------
    `run_directory` : Path
        A path to the directory where flake8 will be executed
    `filename_patterns` : list[str] | None, optional
        A list of glob patterns that will be checked by flake8 (default is
        *.py)
    `flake8_config` : None | Path , optional
        A path to a flake8 config file, where additional configurations can be
        added when flake8 is being executed

    Returns
    -------
    str
        the output from flake8 as a utf-8 str

    Warning
    -------
    Some of possible configurations in the config (`flake8_config`) might
    result in no output, especially if the configuration changes where the
    flake8 writes its output.

    Raises
    ------
    FileNotFoundError:
        If the config file does not exist.

    Available configurations Resources
    ----------------------------------
    https://flake8.pycqa.org/en/latest/user/options.html#index-of-options
    """

    python_command = sys.executable

    flake8_commands = [
        "-m", "flake8"
    ]

    if flake8_config is not None:
        if not flake8_config.exists() or not flake8_config.is_file():
            err = FileNotFoundError(
                errno.ENOENT, os.strerror(errno.ENOENT), flake8_config.name
            )
            err.add_note(
                "There does not exist a flake8 configs file with the name"
                f" `{flake8_config.name}`"
            )
            raise err
        flake8_commands.extend([
            f"--append-config={str(flake8_config.absolute())}",
            "--tee"  # We add this because, in the case the user specified
                     # config specifies a output file, we will still output
                     # to stdout.
        ])

    if filename_patterns is not None:
        flake8_commands.append(
            "--filename=" + (",".join(filename_patterns))
        )

    commands = [python_command]
    commands.extend(flake8_commands)

    proc = subprocess.run(
        commands,
        cwd=str(run_directory),
        capture_output=True
    )

    return proc.stdout.decode()
