from datetime import datetime


def get_time_now(with_seconds: bool = False, with_milliseconds: bool = False) -> str:
    """
    Returns the current time as a string in HH:MM, HH:MM:SS, or HH:MM:SS:MS format.

    Args:
        with_seconds (bool, optional): If True, includes seconds. Defaults to False.
        with_milliseconds (bool, optional): If True, includes milliseconds. Defaults to False.

    Returns:
        str: The formatted current time string.
    """
    now = datetime.now()
    hours = f"{now.hour:02d}"
    minutes = f"{now.minute:02d}"
    seconds = f"{now.second:02d}"
    milliseconds = f"{int(now.microsecond / 1000):02d}"
    time_str = f"{hours}:{minutes}"
    if with_seconds or with_milliseconds:
        time_str += f":{seconds}"
    if with_milliseconds:
        time_str += f":{milliseconds}"
    return time_str
