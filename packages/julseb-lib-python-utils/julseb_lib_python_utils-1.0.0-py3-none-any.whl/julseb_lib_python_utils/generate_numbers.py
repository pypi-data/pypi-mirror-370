def generate_numbers(min_: int = 0, max_: int = 100, step: int = 1) -> list:
    """
    Generates a list of numbers from min to max (inclusive) with a given step.
    """
    return list(range(min_, max_ + 1, step))
