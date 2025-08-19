import random
from datetime import datetime
from typing import Optional


def get_random_date(
    min_year: Optional[int] = None, max_year: Optional[int] = None
) -> str:
    """
        Returns a random date string in YYYY-MM-DD format between min_year and max_year.

        Args:
            min_year (int, optional): Minimum year. Defaults to current year.
            max_year (int, optional): Maximum year. Defaults to current year.

        Returns:
            str: The random date in YYYY-MM-DD format.
    from typing import Optional
    """
    this_year = datetime.now().year
    get_min_year = min_year if min_year is not None else this_year
    get_max_year = max_year if max_year is not None else this_year

    month = random.randint(1, 12)
    if month == 2:
        day = random.randint(1, 28)
    elif month in [4, 6, 9, 11]:
        day = random.randint(1, 30)
    else:
        day = random.randint(1, 31)
    year = random.randint(get_min_year, get_max_year)

    day_str = f"{day:02d}"
    month_str = f"{month:02d}"
    return f"{year}-{month_str}-{day_str}"
