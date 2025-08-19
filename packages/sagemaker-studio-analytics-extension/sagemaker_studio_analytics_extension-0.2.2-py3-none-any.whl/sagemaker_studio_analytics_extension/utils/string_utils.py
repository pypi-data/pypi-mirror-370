def is_not_blank(string):
    return bool(string and string.strip())


def is_blank(string):
    return not is_not_blank(string)


def unquote_ends(string):
    """
    Remove a single pair of quotes from ends of string.
    :param string:
    :return:
    """
    if not string or len(string) < 2:
        return string
    if (string[0] == "'" and string[-1] == "'") or (
        string[0] == '"' and string[-1] == '"'
    ):
        return string[1:-1]
    return string
