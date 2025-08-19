import re
from julseb_lib_python_utils.to_base_case import to_base_case


def to_pascal_case(string: str) -> str:
    """
    Converts a string to PascalCase using to_base_case and regex replacements.

    Args:
        string (str): The input string.

    Returns:
        str: The PascalCase string.
    """
    formatted_string = to_base_case(string)
    s = formatted_string.lower()
    s = re.sub(r"[-_]+", " ", s)
    s = re.sub(r"[^\\w\s]", "", s)
    s = re.sub(r"\s+(.)(\w*)", lambda m: m.group(1).upper() + m.group(2), s)
    s = re.sub(r"\w", lambda m: m.group(0).upper(), s, count=1)
    return s
