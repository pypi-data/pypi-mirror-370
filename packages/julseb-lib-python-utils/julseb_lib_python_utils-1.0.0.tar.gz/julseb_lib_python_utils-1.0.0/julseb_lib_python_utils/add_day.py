from julseb_lib_python_utils.get_today import get_today
from datetime import datetime, timedelta


def add_day(number_of_days: int, date_from: str = get_today()):
    """
    Adds number_of_days to the given date string (YYYY-MM-DD). If no date is provided, uses today's date.
    Returns a datetime.date object.
    """
    if date_from is None:
        date_from = get_today()
    date_obj = datetime.strptime(date_from, "%Y-%m-%d").date()
    new_date = date_obj + timedelta(days=number_of_days)
    return new_date
