from datetime import date


def get_today() -> str:
    """
    Returns today's date as a string in the format 'YYYY-MM-DD'.

    Returns:
        str: The current date formatted as 'YYYY-MM-DD'.
    """
    today = date.today()
    return today.strftime("%Y-%m-%d")
