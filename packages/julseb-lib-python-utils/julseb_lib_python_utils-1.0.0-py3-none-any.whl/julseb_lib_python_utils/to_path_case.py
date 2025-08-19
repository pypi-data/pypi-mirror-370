import re
from julseb_lib_python_utils.to_base_case import to_base_case


def to_path_case(string: str) -> str | None:
    """
    Converts a string to path/case using to_base_case and regex matching.

    Args:
        string (str): The input string.

    Returns:
        str | None: The path/case string, or None if no match.
    """
    formatted_string = to_base_case(string)
    matches = re.findall(
        r"[A-Z]{2,}(?=[A-Z][a-z]+[0-9]*|\b)|[A-Z]?[a-z]+[0-9]*|[A-Z]|[0-9]+",
        formatted_string,
    )
    if not matches:
        return None
    return "/".join(x.lower() for x in matches)
