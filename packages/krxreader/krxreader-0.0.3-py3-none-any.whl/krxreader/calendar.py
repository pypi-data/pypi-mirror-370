import datetime

from krxfetch import calendar


def now() -> datetime.datetime:
    """Return the current korean date and time."""

    return calendar.now()


def is_weekend(dt: datetime.datetime) -> bool:
    """Return whether it is weekend or not."""

    return calendar.is_weekend(dt)


def is_holiday(dt: datetime.datetime) -> bool:
    """Return whether it is holiday or not."""

    return calendar.is_holiday(dt)


def is_closing_day(dt: datetime.datetime) -> bool:
    """Return whether it is a closing day or not."""
    return calendar.is_closing_day(dt)


def is_trading_day(dt: datetime.datetime) -> bool:
    """Return whether it is a trading day or not."""

    return calendar.is_trading_day(dt)
