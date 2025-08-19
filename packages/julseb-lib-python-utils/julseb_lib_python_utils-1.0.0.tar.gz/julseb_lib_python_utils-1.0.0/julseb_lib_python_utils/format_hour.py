def format_hour(hour: float) -> str:
    """
    Formats a float hour as 'HH:MM', matching the TypeScript logic.
    """
    hour_time = f"{int(hour):02d}"
    minutes = "30" if hour % 1 != 0 else "00"
    return f"{hour_time}:{minutes}"
