import random


def get_random_number(min: int = 0, max: int = 100) -> int:
    """
    Returns a random integer between min and max, inclusive.

    Args:
        min (int, optional): Minimum value. Defaults to 0.
        max (int, optional): Maximum value. Defaults to 100.

    Returns:
        int: The random integer.
    """

    return random.randint(min, max)
