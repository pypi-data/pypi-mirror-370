from datetime import datetime, timedelta


def get_yesterday() -> str:
    """
    Returns yesterday's date in YYYY-MM-DD format.

    Returns:
        str: Yesterday's date as a string in YYYY-MM-DD format.
    """
    yesterday = datetime.now() - timedelta(days=1)
    dd = f"{yesterday.day:02d}"
    mm = f"{yesterday.month:02d}"
    yy = yesterday.year
    return f"{yy}-{mm}-{dd}"
