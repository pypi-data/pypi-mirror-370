import string


def count_fstring_variables(text: str) -> int:
    fmt = string.Formatter()

    # formatter.parse returns a 4-tuple: (literal_text, field_name, format_spec, conversion)
    # where `field_name` is not None for any f-string {values}
    count = 0
    for item in fmt.parse(text):
        if item[1] is not None:
            count += 1

    return count
