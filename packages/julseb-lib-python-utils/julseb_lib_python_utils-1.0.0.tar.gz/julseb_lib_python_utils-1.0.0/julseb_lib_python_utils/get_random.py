import random
from typing import Sequence, TypeVar

T = TypeVar("T")


def get_random(array: Sequence[T]) -> T:
    """
    Returns a random element from a non-empty sequence.

    Args:
        array (Sequence[T]): The sequence to pick from.

    Returns:
        T: A random element from the sequence.
    """
    return random.choice(array)
