from typing import Union


def stringify_px(value: Union[int, str]) -> str:
    """
    Converts a value to a string with 'px' appended if it's an integer, or returns the string as is.

    Args:
        value (int | str): The value to stringify.

    Returns:
        str: The stringified value with 'px' if needed.
    """
    if isinstance(value, str):
        return value
    else:
        return f"{value}px"
