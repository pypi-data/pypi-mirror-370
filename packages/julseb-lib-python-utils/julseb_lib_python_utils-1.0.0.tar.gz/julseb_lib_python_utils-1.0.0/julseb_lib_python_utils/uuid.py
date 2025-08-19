import random
import time


def uuid() -> str:
    """
    Generates a pseudo-unique string based on a random number and the current time (milliseconds).

    Returns:
        str: The generated pseudo-unique string.
    """
    return str(random.randint(0, int(time.time() * 1000)))
