from julseb_lib_python_utils.to_sentence_case import to_sentence_case


def unslugify(string: str) -> str:
    """
    Converts a slugified string to sentence case, replacing dashes and underscores with spaces.

    Args:
        string (str): The slugified string.

    Returns:
        str: The unslugified, sentence-cased string.
    """
    return to_sentence_case(string.replace("-", " ").replace("_", " "))
