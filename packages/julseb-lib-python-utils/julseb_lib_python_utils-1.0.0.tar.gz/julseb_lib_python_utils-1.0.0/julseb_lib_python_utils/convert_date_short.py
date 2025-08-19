from datetime import datetime, date


def convert_date_short(input_date) -> str:
    """
    Converts a date (string in 'YYYY-MM-DD' or datetime/date object) to 'DD Mon YYYY' format.
    """
    if isinstance(input_date, str):
        dt = datetime.strptime(input_date, "%Y-%m-%d")
    elif isinstance(input_date, (datetime, date)):
        dt = input_date
    else:
        raise ValueError("input_date must be a string or a date/datetime object")

    months = [
        "Jan",
        "Feb",
        "Mar",
        "Apr",
        "May",
        "Jun",
        "Jul",
        "Aug",
        "Sep",
        "Oct",
        "Nov",
        "Dec",
    ]
    day = f"{dt.day:02d}"
    month = months[dt.month - 1]
    year = str(dt.year)
    return f"{day} {month} {year}"
