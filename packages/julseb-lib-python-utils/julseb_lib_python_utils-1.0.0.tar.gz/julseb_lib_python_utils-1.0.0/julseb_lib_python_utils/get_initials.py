def get_initials(full_name: str) -> str:
    """
    Extracts the initials from a full name.

    Args:
        full_name (str): The full name from which to extract initials.

    Returns:
        str: A string containing the initials of the first and last name.

    Example:
        >>> get_initials("John Doe")
        'JD'
    """
    splitted = full_name.split(" ")
    return f"{splitted[0][0]}{splitted[-1][0]}"
