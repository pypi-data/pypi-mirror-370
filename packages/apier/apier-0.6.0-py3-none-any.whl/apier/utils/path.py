import inspect
import os


def abs_path_from_current_script(rel_path: str) -> str:
    """
    Takes a path relative to the script that is calling this function and
    returns the absolute path.
    """
    caller_script_path = os.path.dirname(inspect.stack()[1][1])
    return os.path.normpath(os.path.join(caller_script_path, rel_path))
