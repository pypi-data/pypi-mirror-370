import locale


def convert_price(price: float, currency: str = "EUR") -> str:
    """
    Formats the price as a currency string using the given currency code.
    """
    try:
        # Set locale to user's default
        locale.setlocale(locale.LC_ALL, "")
    except locale.Error:
        # Fallback to a default locale if user's locale is not supported
        locale.setlocale(locale.LC_ALL, "en_US.UTF-8")

    # Mapping for currency symbols (expand as needed)
    symbols = {
        "EUR": "€",
        "USD": "$",
        "GBP": "£",
        "JPY": "¥",
    }
    symbol = symbols.get(currency, currency)
    formatted = f"{price:,.2f} {symbol}"
    return formatted
