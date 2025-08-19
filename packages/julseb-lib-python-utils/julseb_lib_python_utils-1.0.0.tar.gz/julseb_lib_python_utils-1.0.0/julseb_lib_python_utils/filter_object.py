from typing import Callable


def filter_object(obj: dict, callback: Callable[[tuple, int, list], bool]) -> dict:
    """
    Filters a dictionary based on a callback applied to its entries.
    The callback receives (entry, index, entries) and should return True to keep the entry.
    """

    entries = list(obj.items())
    result = dict(obj)  # shallow copy
    for i, entry in enumerate(entries):
        if not callback(entry, i, entries):
            result.pop(entry[0], None)
    return result
