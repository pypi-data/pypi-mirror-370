def rgb_to_hex(r: int, g: int, b: int) -> str:
    """
    Converts RGB values to a hex color string.

    Args:
        r (int): Red value (0-255).
        g (int): Green value (0-255).
        b (int): Blue value (0-255).

    Returns:
        str: The hex color string (e.g., '#FFAABB').
    """

    def component_to_hex(c: int) -> str:
        hex_str = format(c, "x")
        return hex_str.zfill(2)

    return f"#{component_to_hex(r)}{component_to_hex(g)}{component_to_hex(b)}".upper()
