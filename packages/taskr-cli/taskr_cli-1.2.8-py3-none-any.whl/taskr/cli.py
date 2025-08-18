import argparse
import os
import sys

from .__version__ import version as VERSION
from .taskr import _Taskr


def main() -> None:
    parser = argparse.ArgumentParser(prog="taskr", description="A cli utility to run generic tasks")
    parser.add_argument(
        "-i",
        "--init",
        action="store_true",
        default=False,
        help="generate a template task file",
    )
    parser.add_argument("-l", "--list", action="store_true", help="show defined tasks")
    parser.add_argument("-v", "--version", action="store_true", help="show the version number")
    # TODO
    # parser.add_argument('task', nargs='?', default=None)

    args, custom_args = parser.parse_known_args()

    # No Taskr needed yet
    if args.init:
        _Taskr.init()
        return

    if args.version:
        print(f"Running {VERSION}")
        return

    # Below actions needs an instance of taskr

    try:
        # Attempt to import the tasks file from any sub directory, if we
        # are in a virtual environment with pyenv
        # This could potentially be an issue in certain environments
        root = ""
        if "PYENV_DIR" in os.environ:
            root = os.environ["PYENV_DIR"]
        elif "TASKR_DIR" in os.environ:
            root = os.environ["TASKR_DIR"]

        # Keep going up a directory till we see a tasks.py
        from pathlib import Path

        cur_path = Path(os.getcwd())
        while not os.path.exists(os.path.join(cur_path, "tasks.py")):
            cur_path = cur_path.parent
            if cur_path == Path("/"):
                raise FileNotFoundError("No tasks.py found?")

        if "tasks.py" in os.listdir(cur_path):
            os.chdir(cur_path)

        sys.path.append(root)
        import tasks

    except ImportError:
        print("No valid tasks.py file found in current directory. Run 'taskr --init'")
        parser.print_help()
        sys.exit(1)

    Taskr = _Taskr(tasks)

    # Custom arguments take precedence
    if custom_args:
        task = custom_args.pop(0)
        # Ignore anything that looks like a normal arg, it shouldn't be here
        if task.startswith("-"):
            parser.print_help()
            return

        Taskr.process(task, custom_args)
        return
    elif args.list:
        Taskr.list()
    elif Taskr.hasDefault():
        Taskr.default()
    else:
        parser.print_help()
