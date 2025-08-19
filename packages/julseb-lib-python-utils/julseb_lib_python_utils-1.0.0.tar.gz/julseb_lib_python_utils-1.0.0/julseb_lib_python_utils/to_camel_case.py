import re
from julseb_lib_python_utils.to_base_case import to_base_case


def to_camel_case(string: str) -> str:
    """
    Converts a string to camelCase using to_base_case and regex replacements.

    Args:
        string (str): The input string.

    Returns:
        str: The camelCase string.
    """
    formatted_string = to_base_case(string)
    s = formatted_string.lower()
    s = re.sub(r"[-_]+", " ", s)
    s = re.sub(r"[^\\w\s]", "", s)
    s = re.sub(r"\s+(.)(\w*)", lambda m: m.group(1).upper() + m.group(2), s)
    return s
