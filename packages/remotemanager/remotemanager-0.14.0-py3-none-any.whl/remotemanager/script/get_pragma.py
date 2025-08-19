import re


def get_pragma(line: str) -> str:
    """
    extract the #PRAGMA from line `line`

    returns either #PRAGMA or an empty string
    """
    pragma_pattern = re.compile(r"^#(\w*)\s", re.IGNORECASE)

    match = pragma_pattern.search(line)
    if match:
        if match.groups()[0] == "":
            return ""
        return f"#{match.groups()[0]}"
    else:
        return ""
