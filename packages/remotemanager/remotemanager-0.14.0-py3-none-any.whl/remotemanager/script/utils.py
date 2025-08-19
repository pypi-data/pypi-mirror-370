import logging

from typing import List, Union, Any, TYPE_CHECKING

if TYPE_CHECKING:
    from remotemanager.script.substitution import Substitution
    from remotemanager.script.delayvar import DelayVar

logger = logging.getLogger(__name__)


def format_time(time: Union[int, float, str]) -> Union[str, None]:
    """
    Take integer seconds and generate a HH:MM:SS timestring

    Args:
        time (int):
            seconds
    Returns:
        (str):
            HH:MM:SS format timestamp
    """
    if time is None:
        return None
    if isinstance(time, str):
        # if given a string, first attempt to convert from semantic time
        if "d" in time or "h" in time or "m" in time or "s" in time:
            time = semantic_to_int(time)
        else:
            return time
    elif isinstance(time, float):
        time = int(time)

    return time_to_string(time)


def time_to_string(time: int) -> str:
    """Converts integer seconds to HH:MM:SS format"""
    mins = time // 60
    hours = mins // 60

    secstring = str(time % 60).rjust(2, "0")
    minstring = str(mins % 60).rjust(2, "0")
    hourstring = str(hours).rjust(2, "0")

    return f"{hourstring}:{minstring}:{secstring}"


def time_to_s(time: str) -> int:
    """Convert back from HH:MM:SS to integer seconds"""
    hh, mm, ss = time.split(":")

    return int(hh) * 3600 + int(mm) * 60 + int(ss)


def semantic_to_int(time: str) -> int:
    """
    Convert "semantic" time strings to integer format

    i.e. 24h => 86400, 30m => 1800
    """
    values = {"d": 86400, "h": 3600, "m": 60, "s": 1}

    sum_time = 0
    cache = []
    char = 0
    # iterate over string
    for char in time:
        try:  # store the numbers in the cache
            cache.append(int(char))
        except ValueError:
            # when we hit a non-integer, concat the cache and add it to the sum
            value = int("".join([str(c) for c in cache]))
            cache = []
            if char in values:
                sum_time += values[char] * value

    # convert to integer seconds
    return sum_time


def try_value(inp: Any) -> Any:
    """
    Try to access the value property

    This _needs_ to be used in the presence of DynamicValues, since they override
    a lot of basic functions. This can cause recursion errors if not handled properly
    """
    try:
        return inp.value
    except AttributeError:
        return inp


def _get_expandables(string: str) -> List[str]:
    output = []

    cache = []
    inset = []
    escape = False
    for char in string:
        if char == "\\" and not escape:
            escape = True
            continue

        if not escape:
            if char == "{":
                inset.append("{")

                # do not append the first instance
                if len(inset) == 1:
                    continue

            if char == "}":
                if len(inset) != 0:
                    if inset[-1] == "{":
                        del inset[-1]

                if len(inset) == 0:
                    output.append("".join(cache).strip())
                    cache = []
                    inset = []
                    continue
        else:
            escape = False

        if len(inset) == 0:
            continue

        cache.append(char)

    if len(cache) != 0:
        output.append("".join(cache).strip())

    return output


def concat_basic(
    a: Union[int, "DelayVar", "Substitution"],  # noqa: F821
    b: Union[int, "DelayVar", "Substitution"],  # noqa: F821
) -> Union[int, "DelayVar", "Substitution"]:
    """
    Concat two values a and b

    Required in the case where we want to add a value to a string

    Since str + Resource will call the __add__ method of the str object,
    we get a TypeError

    We need to sidestep this by adding the string to the _value_,
    then reversing the value.

    Doing it this way calls the corrent DynamicMixin.__add__(...) function,
    rather than str.__add__(...)

    ..note::
        This function will at least _try_ to return a+b beforehand

    Args:
        a: first value
        b: second value

    Returns:
        a+b
    """
    logger.debug(
        "Attempting to concat a=%s (type %s), b=%s (type %s)", a, type(a), b, type(b)
    )
    if try_value(a) == "":
        return b
    if try_value(b) == "":
        return a

    try:
        # works only if a is a DynamicMixin instance
        return a + b  # type: ignore
    except TypeError:
        # create the sum in reverse then swap _a and _b
        tmp = b + a  # type: ignore

        b_store = tmp._b  # type: ignore
        tmp._b = tmp._a  # type: ignore
        tmp._a = b_store  # type: ignore

        return tmp
