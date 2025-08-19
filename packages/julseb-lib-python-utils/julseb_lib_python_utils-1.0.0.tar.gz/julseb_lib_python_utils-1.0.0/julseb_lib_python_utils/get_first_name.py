def get_first_name(fullName: str) -> str:
    """
    Extracts and returns the first name from a full name string.

    Args:
        fullName (str): The full name as a single string.

    Returns:
        str: The first name extracted from the full name.
    """

    return fullName.split(" ")[0]
