import random


def get_random_string(length: int = 20, no_numbers: bool = False) -> str:
    """
    Returns a random string of specified length, optionally without numbers.

    Args:
        length (int, optional): Length of the string. Defaults to 20.
        no_numbers (bool, optional): If True, excludes numbers. Defaults to False.

    Returns:
        str: The random string.
    """
    random_chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"
    numbers = "0123456789"
    full_string = random_chars if no_numbers else random_chars + numbers
    return "".join(random.choice(full_string) for _ in range(length))
