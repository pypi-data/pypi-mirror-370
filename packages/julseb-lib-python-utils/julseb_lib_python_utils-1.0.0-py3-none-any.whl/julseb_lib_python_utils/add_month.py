from datetime import datetime
from julseb_lib_python_utils.get_today import get_today


def add_month(number_of_months: int, date_from: str = get_today()):
    """
    Adds number_of_months to the given date string (YYYY-MM-DD). If no date is provided, uses today's date.
    Returns a datetime.date object.
    """
    date_obj = datetime.strptime(date_from, "%Y-%m-%d").date()
    # Calculate new month and year
    month = date_obj.month - 1 + number_of_months
    year = date_obj.year + month // 12
    month = month % 12 + 1
    day = min(
        date_obj.day,
        [
            31,
            29 if year % 4 == 0 and (year % 100 != 0 or year % 400 == 0) else 28,
            31,
            30,
            31,
            30,
            31,
            31,
            30,
            31,
            30,
            31,
        ][month - 1],
    )
    return date_obj.replace(year=year, month=month, day=day)
