from julseb_lib_python_utils.to_base_case import to_base_case


def to_sentence_case(string: str) -> str:
    """
    Converts a string to Sentence case using to_base_case.

    Args:
        string (str): The input string.

    Returns:
        str: The sentence case string.
    """
    formatted_string = to_base_case(string)
    formatted_string = formatted_string.lower()
    if not formatted_string:
        return ""
    return formatted_string[0].upper() + formatted_string[1:]
