import random


def get_random_time(min: int = 0, max: int = 23, with_seconds: bool = False) -> str:
    """
    Returns a random time string in HH:MM or HH:MM:SS format.

    Args:
        min (int, optional): Minimum hour. Defaults to 0.
        max (int, optional): Maximum hour. Defaults to 23.
        with_seconds (bool, optional): If True, includes seconds. Defaults to False.

    Returns:
        str: The random time string.
    """

    hour = random.randint(min, max)
    minutes = random.randint(0, 59)
    seconds = random.randint(0, 59)
    hour_str = f"{hour:02d}"
    minutes_str = f"{minutes:02d}"
    seconds_str = f"{seconds:02d}"
    if with_seconds:
        return f"{hour_str}:{minutes_str}:{seconds_str}"
    else:
        return f"{hour_str}:{minutes_str}"
