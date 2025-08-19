from julseb_lib_python_utils.slugify import slugify


def to_kebab_case(string: str) -> str:
    """
    Converts a string to kebab-case using slugify.

    Args:
        string (str): The input string.

    Returns:
        str: The kebab-case string.
    """
    return slugify(string)
