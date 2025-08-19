def get_last_name(full_name: str) -> str:
    """
    Returns the last name from a full name string.

    Args:
        full_name (str): The full name as a string.

    Returns:
        str: The last name extracted from the full name.
    """

    split = full_name.split(" ")
    return split[-1]
