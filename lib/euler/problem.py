from functools import cached_property
from itertools import takewhile
import importlib.util as importlib
import inspect
import os
import sys
import uuid
import re

from .definitions import DATA_DIR, DESK_DIR, DRAWER_DIR, SOLVED_DIR


DIRECTORIES = [
    DESK_DIR,
    SOLVED_DIR,
    DRAWER_DIR
]


def _problem_number_from_path(path):
    filename = os.path.basename(path)
    number = os.path.splitext(filename)[0]

    try: return int(number)
    except ValueError:
        return None


class Script:
    def __init__(self, file=None, *, number=None):
        if (file is None) == (number is None):
            raise TypeError("__init__() requires exactly one argument")

        filename = str(file if number is None else number)

        if not filename.lower().endswith('.py'):
            filename += '.py'

        path = os.path.abspath(filename)

        if not os.path.exists(path):
            for directory in [ os.getcwd(), *DIRECTORIES ]:
                path = os.path.abspath(os.path.join(directory, filename))
                if os.path.exists(path):
                    break
                path = None

        if not path:
            raise Exception("Unable to locate file {}".format(filename))

        self._path = path

    @property
    def path(self):
        return self._path

    @cached_property
    def problem_number(self):
        return _problem_number_from_path(self.path)

    @cached_property
    def uuid(self):
        class_name = self.__class__.__name__
        return uuid.uuid3(uuid.UUID(int=self.problem_number), class_name)

    @cached_property
    def module_name(self):
        return 'p{}-{}'.format(self.problem_number, self.uuid.bytes.hex())

    def create_module(self):
        spec = importlib.spec_from_file_location(self.module_name, self.path)
        module = importlib.module_from_spec(spec)
        spec.loader.exec_module(module)

        return module


class Problem:
    def __init__(self, module):
        self._module = module

        if not hasattr(module, 'solve') or not callable(module.solve):
            raise Exception("Module does not have a solve() function")

        if not hasattr(module, 'solution'):
            raise Exception("Module does not have a 'solution' variable")

        if not hasattr(module, 'args'):
            raise Exception("Module does not have an 'args' variable")

        if not isinstance(module.args, tuple):
            raise Exception("The module's 'args' variable "
                            "is required to be a tuple")

        # TODO: add optional **kwargs

        try:
            inspect.signature(module.solve).bind(*module.args)
        except TypeError as e:
            raise Exception("The module's function signature of solve() is "
                            "not compatible with the values in 'args'") from e

        # register the module so that it can be imported if necessary.
        # e.g. the pickle library can't dump classes that it cannot import.
        sys.modules[module.__name__] = module

        # NOTE: we should theoretically unregister the module after usage

    @classmethod
    def from_file(cls, filename):
        return Problem(Script(filename).create_module())

    @classmethod
    def from_number(cls, number):
        return cls.from_file(number)

    @classmethod
    def from_script(cls, script):
        return Problem(script.create_module())

    @cached_property
    def number(self):
        return _problem_number_from_path(self.module.__file__)

    @property
    def module(self):
        return self._module

    @property
    def solution(self):
        return self.module.solution

    @property
    def solve_function(self):
        return self.module.solve

    @property
    def args(self):
        return self.module.args

    @property
    def is_solved(self):
        return self.solution is not None

    def solve(self):
        return self.solve_function(*self.args)


class LazyProblemModule:
    def __init__(self, filename):
        self._filename = filename
        self._problem = None

    def _init_problem(self):
        self._problem = Problem.from_file(self._filename)

    def __getattr__(self, name):
        if not self._problem:
            self._init_problem()
        return getattr(self._problem.module, name)


class Data:
    def __init__(self, problem_filename=None):
        paths = [ problem_filename ]

        if not problem_filename:
            paths = [ s[1] for s in reversed(inspect.stack()) ]

        for path in paths:
            try:
                script = Script(path)
            except Exception:
                continue

            if script.problem_number is not None:
                self._problem_number = script.problem_number
                return

            # TODO: throw below exception in Script() and
            #   reraise if no valid path has been found.

        raise Exception('Expected file to be named N.py, '
                        'with N being an integer')


    def read(self, filename):
        problem = str(self._problem_number)
        filename = os.path.join(DATA_DIR, problem, filename)

        with open(filename, 'r') as file:
            return file.read()


def read_data(filename, problem_filename=None):
    return Data(problem_filename).read(filename)


def iterate_solved_scripts():
    def keyfunc(x):
        if x[0].isdigit():
            return int(''.join(takewhile(str.isdigit, x)))
        return 0

    for filename in sorted(os.listdir(SOLVED_DIR), key=keyfunc):
        match = re.match(r'([0-9]+).py', filename)
        if match:
            number = int(match.groups()[0])
            yield number, filename
