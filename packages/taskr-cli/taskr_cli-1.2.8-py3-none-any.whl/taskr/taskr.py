import os
import sys
from contextlib import suppress
from dataclasses import dataclass
from importlib.machinery import ModuleSpec, PathFinder
from inspect import getattr_static, getcomments, getdoc, getmembers, isfunction
from types import ModuleType
from typing import Any, Callable, Dict, List, Optional, Tuple

from .utils import inVenv, readEnvFile


class _CustomFinder(PathFinder):
    """
    Allows us to import a file in the current directory, that is
    the directory the file is run in. the tasks.py file should
    always be run from it's own dir, for now

    https://stackoverflow.com/a/44788410
    """

    _path = [os.getcwd()]

    @classmethod
    def find_spec(
        cls: Any, fullname: Any, path: Any = None, target: Any = None
    ) -> Optional[ModuleSpec]:
        return super().find_spec(fullname, cls._path, target)


sys.meta_path.append(_CustomFinder)


# Mainly so mypy doesn't yell about lambdas
def _dummy() -> bool:
    return True


@dataclass
class _Function:
    """Used to hold useful information on a function from tasks.py"""

    name: str = ""
    func: Callable[[], bool] = _dummy
    defaults: Optional[Tuple[Any]] = None
    argnames: Optional[Tuple[str, ...]] = None


class _Taskr:
    """
    The general flow from invocation of a taskr, to showing a task
    - Check if we should enforce being in a venv

    - Populate environment variables from a file, if set

    - Populate internal lists of tasks
     - Grab a list of members from the module
     - Remove any that aren't defined in tasks.py (imported, etc)
     - Remove any that start with '_'

    - Map the function name to an object with it's callable,
      and meta data on it

    - When a task is passed, then
     - Make sure it exists in our mapping
     - Set environment variables if the user set them above
     - If custom args are passed, make sure they passed correct ones
     - Send them to our mapped function


    """

    def __init__(self, module: ModuleType) -> None:
        self.funcs: Dict[str, _Function] = {}
        self._module = module

        # Settings from tasks.py
        self.envs: Optional[Dict[str, str]] = None
        self.venv_required: Optional[str] = None
        self.default_function: Optional[str] = None
        self._populate_settings()

        # Do some pre-checks, then process everything in the module
        self._enforce_venv()
        self._get_tasks()

    def _populate_settings(self) -> None:
        """
        Populate values of possible settings in task.py
        """

        # Reads in a user set environment file if it's set in tasks.py
        # Example: "ENVS = 'dev.env'"
        # Sets it before running a tasks
        # TODO - write down why these are exceptions
        with suppress(AttributeError):
            self.envs = readEnvFile(getattr_static(self._module, "ENVS"))

        # Should taskr not run unless it's in a venv
        with suppress(AttributeError):
            self.venv_required = getattr_static(self._module, "VENV_REQUIRED")

        # Is there a default task?
        with suppress(AttributeError):
            self.default_function = getattr_static(self._module, "DEFAULT")

    def _enforce_venv(self) -> None:
        """
        Looks to see if the tasks file requires the user to be in a venv
        """
        if self.venv_required is not None and not inVenv():
            print("Not currently in a virtual environment, stopping")
            sys.exit(1)

    def _get_tasks(self) -> None:
        """
        Internal function that pulls every function from a module
        and matches it with a name, basically the core
        """
        funcs = getmembers(self._module, isfunction)
        for func in funcs:
            # Skip 'unexported' functions
            if func[0].startswith("_"):
                continue

            # Skip functions that have been imported
            if func[1].__module__ != "tasks":
                continue

            self.funcs[func[0]] = _Function(
                name=func[0],
                func=func[1],
                defaults=func[1].__defaults__,
                argnames=func[1].__code__.co_varnames[: func[1].__code__.co_argcount],
            )

    @staticmethod
    def init() -> None:
        """
        Generates a default task file
        """
        from taskr.template import template

        filename = "tasks.py"

        if os.path.exists(filename):
            print("Task file already exists, skipping generation")
            return

        with open(filename, "w") as file:
            file.write(template)

        print(f"Generated sample task file {filename}")

    def list(self) -> None:
        """
        Lists available tasks

        On initialization we get a dictionary of names to functions
        This will loop through the names, and try to grab the doc strings
        of the functions and display them

        If there is a default function defines, we mark it
        """
        if len(self.funcs) == 0:
            print("No tasks defined or found in tasks.py")
            return

        print("\nTasks and arguments:")

        display = {}
        for name, func_attrs in self.funcs.items():
            newName = name
            if name == self.default_function:
                newName = f"*{name}"

            # Display arguments if the task takes them
            if func_attrs.argnames:
                newName = f"{name}: {', '.join(func_attrs.argnames)}"

            # Try to find documentation for the function
            # If both exist, show the single # comment so the doc block
            # can be used for documentation
            doc = None
            docString = getdoc(func_attrs.func)  # Regular dock block
            docPreceed = getcomments(func_attrs.func)  # Single line #
            if docString:
                doc = docString.replace("\n", "").strip()
            if docPreceed:
                doc = docPreceed.replace("#", "").strip()
            if not doc:
                doc = "No comment"

            display[newName] = doc

        maxName = max(display.keys(), key=len)
        for name, doc in display.items():
            print(f" {name:<{len(maxName)+1}}: {doc}")

        print("\n* = default")

    def _grabKwargs(self, userArgs: List[str]) -> Tuple[List[str], Dict[str, str]]:
        """
        Split up arguments that a user passes in to be key word or not
        # TODO - ints
        """
        kwargs = {}
        newAgs = []
        for arg in userArgs:
            # Just assume the user formats it right, for now
            # Could be a regex probably
            if isinstance(arg, str) and "=" in arg:
                k, v = arg.split("=")
                kwargs[k.strip()] = v.strip()
            else:
                newAgs.append(arg)

        return newAgs, kwargs

    def process(self, task: str, args: Optional[List[str]] = None) -> None:
        """
        Given a task name, runs the function if it exists
        If a task that takes arguments is passed
            - make sure that only the correct amount is passed
            - can allow no args passed
        If a task that takes no arguments is passed
            - ignore all args after it
        """
        known = self.funcs.get(task)
        if known:
            try:
                # Apply default env vars is user has them set
                # This happens before runners copies the systems envs, so
                # these are copied over
                # TODO - add tests?
                if self.envs:
                    for k, v in self.envs.items():
                        os.environ[k] = v
                if args and known.argnames:
                    if len(args) > len(known.argnames):
                        print("Warning - More arguments passed than task takes. Skipping")
                        return

                    args, kwargs = self._grabKwargs(args)

                    # TODO - make sure keys are in known.args
                    known.func(*args, **kwargs)

                else:
                    known.func()
            except Exception as e:
                print(f"Error running task {task}: {e}")
        else:
            print(f"Unknown task: {task}")

    def hasDefault(self) -> bool:
        """
        Let's the CLI know if we can run a default command
        """
        return self.default_function is not None

    def default(self) -> bool:
        """
        Runs the default task, if it's defined
        """
        if self.default_function:
            if self.default_function not in self.funcs:
                print(f"Default task {self.default_function} is not defined")
                return False

            self.funcs.get(self.default_function).func()  # type: ignore
            return True
        else:
            print("No default defined")
            return False
