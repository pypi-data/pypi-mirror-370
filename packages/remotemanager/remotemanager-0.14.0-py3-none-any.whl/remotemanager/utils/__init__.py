import gc
import math
import os
import random
import re
import time
from typing import Union, Any

_time_format = "%Y-%m-%d %H:%M:%S"


def ensure_list(inp: Any = None, semantic: bool = False) -> list:
    """
    Ensure that `inp` is list-type

    .. note::
        None is a special case, returning an empty list, rather than [None]

    Args:
        inp:
            list, string, object to be processed
        semantic (bool):
            attempts to treat comma (or space) separated strings as lists
            e.g. "a,b,c" will return ["a", "b", "c"]

    Returns (list):
        Either inserts the object into a list, or returns the list-like inp
    """
    if inp is None:
        return []
    if isinstance(inp, dict):
        return [inp]
    if isinstance(inp, (list, tuple, set)):
        return list(inp)
    if isinstance(inp, (str, int, float)) and not semantic:
        return [inp]

    if semantic and isinstance(inp, str):
        # a "semantic" list is used for situations like template `replaces`
        # and should handle comma/space separated "lists" in a string
        if "," in inp:
            splitchar = ","
        else:
            splitchar = None
        return [item.strip() for item in inp.split(splitchar)]

    try:
        return list(inp)
    except TypeError:
        return [inp]


def ensure_filetype(file: str, target_type: Union[str, None]):
    """
    Ensure that `file` is of type `type`

    Args:
        file (str):
            filename
        target_type (str):
            filetype to enforce

    Returns (str):
        filename of type `type`
    """
    fname, ftype = os.path.splitext(file)

    if target_type is None:
        return fname

    target_type = target_type.strip(".")

    return f"{fname}.{target_type}"


def ensure_dir(dir):
    """
    Ensure that string path to `dir` is correctly formatted
    ONLY ensures that the folder name ends with a "/", does not produce an
    abspath

    Args:
        dir (str):
            path to dir

    Returns (str):
        ensured dir path
    """
    return os.path.join(dir, " ").strip()


def safe_divide(a: Union[float, int], b: Union[float, int]) -> Union[float, int]:
    """
    Always-fit division. Rounds up after division, returns >= 1

    Args:
        a (num):
            numerator
        b (num):
            denominator

    Returns:
        result of a/b division, unless result returns <1, else 1
    """
    if b == 0:
        return 1
    r = math.ceil(a / b)
    return max(r, 1)


def get_version() -> str:
    """
    Gets the current package version from __init__.py
    """

    from remotemanager import __version__

    return __version__


def recursive_dict_update(d1: dict, d2: dict) -> dict:
    """
    Update d1 with all the keys of d2

    Args:
        d1 (dict):
            dictionary to be updated
        d2 (dict):
            dictionary to update with

    Returns (dict):
        updated d1
    """
    if not isinstance(d1, dict):
        return d2

    for k, v in d2.items():
        if isinstance(v, dict) and k in d1:
            d1[k] = recursive_dict_update(d1[k], d2[k])
        else:
            d1[k] = v

    return d1


def reverse_index(inplist: list, term):
    """
    return index of last occurrence of `term` in `inplist`

    Args:
        inplist (list):
            list to index
        term:
            object to index

    Returns (int):
        forward index of item
    """
    return len(inplist) - inplist[::-1].index(term) - 1


def integer_time_wait(offset: float = 0.0) -> None:
    """
    wait for an integer unix time + offset

    This function exists to increase the reproducibility of the tests

    Args:
        offset (float):
            extra offset to wait for
    """

    t0 = time.time()

    wait = 1 - math.fmod(t0, 1)

    time.sleep(wait + offset)

    return None


def object_from_uuid(uuid: str, name: str):
    """
    Search the memory heap for an object of uuid `uuid` and classname
    `name`

    for example;

    >>> recovered_dataset = object_from_uuid("<uuid>", "Dataset")

    Args:
        uuid:
            uuid target
        name:
            classname to search for

    Returns:
        object instance matching input, if it exists
    """

    for obj in gc.get_objects():
        try:
            if obj.__class__.__name__ == name:
                if obj.uuid == uuid:
                    return obj
        except AttributeError:
            pass

    raise ValueError(f"could not find {name} in memory with UUID {uuid}")


def dir_delta(base: str, test: str) -> int:
    """
    Counts the directory level difference between `base` and `test`

    e.g:
    if `base` is a _subdirectory_ of `test`, the number will be -ve

    Args:
        base:
            base directory to test from
        test:
            directory to query

    Returns:
        int
    """
    # make sure we have abspaths for commonprefix
    base = os.path.abspath(base)
    test = os.path.abspath(test)
    # if the paths are equal, return False
    if base == test:
        return 0
    # get the common part of the path to remove
    mix = os.path.commonpath([base, test])
    # delete the common from both paths
    diff_neg = len(base.replace(mix, "").split(os.sep))
    diff_pos = len(test.replace(mix, "").split(os.sep))

    return diff_pos - diff_neg


def check_dir_is_child(base: str, test: str) -> bool:
    """
    Makes sure that `test` is a child leaf directory of `base`

    Args:
        base:
            base directory to test from
        test:
            directory to query

    Returns:
        bool
    """
    # make sure we have abspaths for commonprefix
    base = os.path.abspath(base)
    test = os.path.abspath(test)
    # if the paths are equal, return False
    if base == test:
        return False
    # get the common part of the path to remove
    mix = os.path.commonpath([base, test])
    # delete the common from both paths
    diff_neg = base.replace(mix, "").split(os.sep)

    diff_num = 1 - len(diff_neg)
    return diff_num >= 0


def extract_bash_variables(string: str) -> list:
    """
    Given a string containing bash $VARIABLES, extract a list of those variables

    Special case for a string starting with the $HOME shortcut `~`

    Args:
        string:
            bash string

    Returns:
        list of variables
    """
    pattern = r"\$[A-Za-z_][A-Za-z_0-9]*|\${[A-Za-z_][A-Za-z_0-9]*}"

    variables = re.findall(pattern, string)

    if string.startswith("~"):
        variables.insert(0, "~")
    return variables


def random_string(len: int = 16) -> str:
    """Creates a random string of hexadecimal characters of len `len`"""
    choices = list(range(9)) + ["a", "b", "c", "d", "e", "f"]
    output = []
    for i in range(len):
        output.append(str(random.choice(choices)))

    return "".join(output)
