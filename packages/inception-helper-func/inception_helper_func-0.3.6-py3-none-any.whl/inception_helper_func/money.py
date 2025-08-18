import locale
from contextlib import contextmanager


@contextmanager
def set_temp_locale(loc: str):
    """Context manager to temporarily set the locale."""
    saved = locale.getlocale(locale.LC_ALL)
    try:
        locale.setlocale(locale.LC_ALL, loc)
        yield
    finally:
        locale.setlocale(locale.LC_ALL, saved)


def fmt(amount: float, loc: str = "en_US") -> str:
    """
    Formats the amount as money, including two decimal places and thousands separator.
    :param amount: The amount to format.
    :param loc: The locale to use for formatting (default is 'en_US').
    :return: The formatted amount as a string.
    """
    with set_temp_locale(loc):
        return locale.format_string("%.2f", amount, grouping=True)


def fmt_with_currency(amount: float, currency: str, loc: str = "en_US") -> str:
    """
    Formats the amount as money, including two decimal places and thousands separator, and adds the currency symbol.
    :param amount: The amount to format.
    :param currency: The currency symbol (e.g., "$", "€").
    :param loc: The locale to use for formatting (default is 'en_US').
    :return: The formatted amount with the currency symbol or currency code.
    """
    return f"{currency} {fmt(amount, loc)}"


if __name__ == "__main__":
    # Example usage
    print(fmt(123456789.123456789, "en_US"))
    print(fmt_with_currency(123456789.123456789, "$", "en_US"))
    print(fmt(123456789.123456789, "es_ES"))
    print(fmt_with_currency(123456789.123456789, "€", "es_ES"))
    print(fmt(123456789.123456789, "fr_FR"))
    print(fmt_with_currency(123456789.123456789, "€", "fr_FR"))
    print(fmt(123456789.123456789, "de_DE"))
    print(fmt_with_currency(123456789.123456789, "€", "de_DE"))
    print(fmt(123456789.123456789, "it_IT"))
    print(fmt_with_currency(123456789.123456789, "€", "it_IT"))
