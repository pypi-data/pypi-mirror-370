from datetime import datetime, date


def convert_date(input_date) -> str:
    """
    Converts a date (string in 'YYYY-MM-DD' or datetime/date object) to 'DD Month YYYY' format.
    """
    if isinstance(input_date, str):
        dt = datetime.strptime(input_date, "%Y-%m-%d")
    elif isinstance(input_date, (datetime, date)):
        dt = input_date
    else:
        raise ValueError("input_date must be a string or a date/datetime object")

    months = [
        "January",
        "February",
        "March",
        "April",
        "May",
        "June",
        "July",
        "August",
        "September",
        "October",
        "November",
        "December",
    ]
    day = f"{dt.day:02d}"
    month = months[dt.month - 1]
    year = str(dt.year)
    return f"{day} {month} {year}"
