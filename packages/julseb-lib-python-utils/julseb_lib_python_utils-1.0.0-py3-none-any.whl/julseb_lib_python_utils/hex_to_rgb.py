import re


def hex_to_rgb(hex_str: str) -> str | None:
    """
    Converts a hex color string to an RGB string in the format (r, g, b).

    Args:
        hex_str (str): The hex color string (e.g., '#FFAABB' or 'FFAABB').

    Returns:
        str | None: The RGB string or None if the input is invalid.
    """
    match = re.fullmatch(r"#?([a-fA-F\d]{2})([a-fA-F\d]{2})([a-fA-F\d]{2})", hex_str)
    if not match:
        return None
    r = int(match.group(1), 16)
    g = int(match.group(2), 16)
    b = int(match.group(3), 16)
    return f"({r}, {g}, {b})"
