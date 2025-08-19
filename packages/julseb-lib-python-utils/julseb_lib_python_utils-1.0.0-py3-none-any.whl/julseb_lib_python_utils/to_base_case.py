import re


def to_base_case(string: str) -> str:
    """
    Converts a string to base case (lowercase, spaces between camel case, replaces accented/special chars).

    Args:
        string (str): The input string.

    Returns:
        str: The base case string.
    """
    splitted = re.sub(r"\.?(?=[A-Z])", " ", string).lower()
    from_chars = "àáäâèéëêìíïîòóöôùúüûñç·/_,:;-"
    to_chars = "aaaaeeeeiiiioooouuuunc-- --- "
    trans_table = str.maketrans(from_chars, to_chars)
    splitted = splitted.translate(trans_table)
    return splitted
