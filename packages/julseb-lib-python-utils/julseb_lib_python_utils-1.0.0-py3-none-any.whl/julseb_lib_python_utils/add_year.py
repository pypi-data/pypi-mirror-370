from julseb_lib_python_utils.get_today import get_today
from datetime import datetime


def add_year(number_of_years: int, date_from: str = get_today()):
    """
    Adds number_of_years to the given date string (YYYY-MM-DD). If no date is provided, uses today's date.
    Returns a datetime.date object.
    """
    date_obj = datetime.strptime(date_from, "%Y-%m-%d").date()
    try:
        return date_obj.replace(year=date_obj.year + number_of_years)
    except ValueError:
        # Handle February 29th on non-leap years
        return date_obj.replace(month=2, day=28, year=date_obj.year + number_of_years)
