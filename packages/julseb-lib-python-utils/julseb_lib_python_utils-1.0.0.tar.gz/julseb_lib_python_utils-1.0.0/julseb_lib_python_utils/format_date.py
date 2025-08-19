from datetime import datetime, date


def format_date(input_date) -> str:
    """
    Formats a date (string or date/datetime object) as 'YYYY-MM-DD'.
    """
    if isinstance(input_date, str):
        dt = datetime.fromisoformat(input_date)
    elif isinstance(input_date, (datetime, date)):
        dt = input_date
    else:
        raise ValueError("input_date must be a string or a date/datetime object")
    return dt.strftime("%Y-%m-%d")
