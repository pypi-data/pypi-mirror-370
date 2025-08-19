def calculate_average(arr: list[int]) -> float:
    """
    Calculates the average (arithmetic mean) of a list of integers.

    Args:
        arr (list[int]): A list of integers to calculate the average of.

    Returns:
        float: The average of the integers in the list. Returns 0 if the list is empty.
    """
    if not arr:
        return 0
    return sum(arr) / len(arr)
