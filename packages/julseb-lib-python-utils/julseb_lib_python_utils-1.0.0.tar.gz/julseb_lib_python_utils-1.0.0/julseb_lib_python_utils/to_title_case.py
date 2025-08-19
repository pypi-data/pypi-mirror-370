from julseb_lib_python_utils.to_base_case import to_base_case


def to_title_case(string: str) -> str:
    """
    Converts a string to Title Case using to_base_case.

    Args:
        string (str): The input string.

    Returns:
        str: The title case string.
    """
    formatted_string = to_base_case(string)
    arr = formatted_string.lower().split(" ")
    arr = [word.capitalize() for word in arr]
    return " ".join(arr)
