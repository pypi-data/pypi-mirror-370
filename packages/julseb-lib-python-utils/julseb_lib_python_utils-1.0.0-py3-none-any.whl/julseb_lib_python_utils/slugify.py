import re


def slugify(string: str) -> str:
    """
    Converts a given string into a URL-friendly slug.

    This function transforms the input string by:
    - Converting it to lowercase.
    - Replacing spaces with hyphens.
    - Removing leading and trailing whitespace.
    - Replacing accented and special characters with their ASCII equivalents.
    - Removing any remaining non-alphanumeric characters (except hyphens).
    - Replacing multiple spaces or hyphens with a single hyphen.

    Args:
        string (str): The input string to be slugified.

    Returns:
        str: The slugified version of the input string.
    """
    formatted_string = string.lower().replace(" ", "-")
    formatted_string = formatted_string.strip()
    formatted_string = formatted_string.lower()

    from_chars = "àáäâèéëêìíïîòóöôùúüûñç·/_,:;-"
    to_chars = "aaaaeeeeiiiioooouuuunc------"
    trans = str.maketrans(from_chars, to_chars)
    formatted_string = formatted_string.translate(trans)

    formatted_string = re.sub(r"[^a-z0-9 -]", "", formatted_string)
    formatted_string = re.sub(r"\s+", "-", formatted_string)
    formatted_string = re.sub(r"-+", "-", formatted_string)
    return formatted_string
