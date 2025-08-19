from datetime import datetime, timedelta


def get_tomorrow() -> str:
    """
    Returns tomorrow's date in YYYY-MM-DD format.

    Returns:
        str: Tomorrow's date as a string in YYYY-MM-DD format.
    """
    tomorrow = datetime.now() + timedelta(days=1)
    dd = f"{tomorrow.day:02d}"
    mm = f"{tomorrow.month:02d}"
    yy = tomorrow.year
    return f"{yy}-{mm}-{dd}"
