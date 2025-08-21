from pathlib import Path
from contextlib import contextmanager
import dateparser
import os

@contextmanager
def cd(path):
    """Sets the cwd within the context
    """
    origin = Path().resolve()
    try:
        os.chdir(path)
        yield
    finally:
        os.chdir(origin)

def in_bounds(value, minimum=None, maximum=None):
    return (not minimum or value >= minimum) and (not maximum or value <= maximum)

def date_string(arg):
    return dateparser.parse(arg, settings={'RETURN_AS_TIMEZONE_AWARE': True})

