from datetime import datetime, timedelta


def get_next_day(current_date: str | datetime) -> str:
    """
    Returns the next day's date in YYYY-MM-DD format given a date string or datetime object.

    Args:
        current_date (str | datetime): The current date as a string or datetime object.

    Returns:
        str: The next day's date in YYYY-MM-DD format.
    """
    if isinstance(current_date, str):
        today = datetime.fromisoformat(current_date)
    else:
        today = current_date
    next_date = today + timedelta(days=1)
    dd = f"{next_date.day:02d}"
    mm = f"{next_date.month:02d}"
    yy = next_date.year
    return f"{yy}-{mm}-{dd}"
