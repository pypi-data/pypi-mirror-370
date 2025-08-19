def capitalize(string: str) -> str:
    """
    Returns the string with the first character capitalized.
    """
    if not string:
        return ""
    return string[0].upper() + string[1:]
