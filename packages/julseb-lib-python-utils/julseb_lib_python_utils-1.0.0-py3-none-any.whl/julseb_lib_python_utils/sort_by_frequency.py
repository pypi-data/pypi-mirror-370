from typing import List, Any


def sort_by_frequency(array: List[Any]) -> List[str]:
    """
    Sorts an array of items by their frequency (descending), then alphabetically if frequencies are equal.

    Args:
        array (List[Any]): The input array of items (should be string-like).

    Returns:
        List[str]: The unique values sorted by frequency and then alphabetically.
    """
    frequency = {}
    for item in array:
        value = str(item).lower()
        frequency[value] = frequency.get(value, 0) + 1
    uniques = list(frequency.keys())
    uniques.sort(key=lambda x: (-frequency[x], x))
    return uniques
